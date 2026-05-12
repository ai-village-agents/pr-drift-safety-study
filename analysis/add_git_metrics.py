#!/usr/bin/env python3
"""Add git-derived PR metrics for the Universe PR drift study.

Inputs:
  - data/raw_prs.jsonl from this repository
  - a local clone of ai-village-agents/the-universe with PR refs fetched

Outputs:
  - results/git_pr_metrics.csv

The GitHub API file summaries are useful, but they are a server-side summary of
base..head. This script independently asks git about every PR's base/head SHAs:
commit availability, ahead/behind counts, exact numstat/name-status totals, file
touch indicators, and (when main.js is available) a deterministic count of
objects inside the cosmicSights array at base and head.
"""
from __future__ import annotations

import argparse
import csv
import json
import os
import subprocess
import sys
from functools import lru_cache
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data"
RESULTS = ROOT / "results"
RESULTS.mkdir(exist_ok=True)

DEFAULT_UNIVERSE = Path(os.environ.get("UNIVERSE_REPO", "/home/computeruse/the-universe"))


def load_jsonl(path: Path):
    return [json.loads(line) for line in path.read_text().splitlines() if line.strip()]


class Git:
    def __init__(self, repo: Path, timeout: int = 20):
        self.repo = Path(repo)
        self.timeout = timeout

    def run(self, *args: str, check: bool = False) -> subprocess.CompletedProcess:
        cp = subprocess.run(
            ["git", "-C", str(self.repo), *args],
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            timeout=self.timeout,
        )
        if check and cp.returncode != 0:
            raise RuntimeError(f"git {' '.join(args)} failed: {cp.stderr.strip()}")
        return cp

    @lru_cache(maxsize=None)
    def exists(self, sha: str | None) -> bool:
        if not sha:
            return False
        cp = self.run("cat-file", "-e", f"{sha}^{{commit}}")
        return cp.returncode == 0

    @lru_cache(maxsize=None)
    def merge_base(self, base: str, head: str) -> str:
        cp = self.run("merge-base", base, head)
        return cp.stdout.strip() if cp.returncode == 0 else ""

    @lru_cache(maxsize=None)
    def is_ancestor(self, base: str, head: str) -> bool | None:
        cp = self.run("merge-base", "--is-ancestor", base, head)
        if cp.returncode == 0:
            return True
        if cp.returncode == 1:
            return False
        return None

    @lru_cache(maxsize=None)
    def rev_counts(self, base: str, head: str) -> tuple[int | None, int | None]:
        cp = self.run("rev-list", "--left-right", "--count", f"{base}...{head}")
        if cp.returncode != 0:
            return None, None
        parts = cp.stdout.strip().split()
        if len(parts) != 2:
            return None, None
        # For base...head: left=commits in base not head (behind), right=head not base (ahead).
        return int(parts[0]), int(parts[1])

    @lru_cache(maxsize=None)
    def diff_numstat(self, base: str, head: str) -> tuple[int, int, int]:
        cp = self.run("diff", "--numstat", f"{base}..{head}")
        if cp.returncode != 0:
            return 0, 0, 0
        files = additions = deletions = 0
        for line in cp.stdout.splitlines():
            parts = line.split("\t")
            if len(parts) < 3:
                continue
            files += 1
            a, d = parts[0], parts[1]
            if a != "-":
                additions += int(a)
            if d != "-":
                deletions += int(d)
        return files, additions, deletions

    @lru_cache(maxsize=None)
    def diff_name_status(self, base: str, head: str) -> tuple[tuple[str, str], ...]:
        cp = self.run("diff", "--name-status", f"{base}..{head}")
        if cp.returncode != 0:
            return tuple()
        rows = []
        for line in cp.stdout.splitlines():
            parts = line.split("\t")
            if len(parts) >= 2:
                # Renames/copies include old and new names; use the destination path for touch flags.
                rows.append((parts[0], parts[-1]))
        return tuple(rows)

    @lru_cache(maxsize=None)
    def show_file(self, sha: str, path: str) -> str | None:
        cp = self.run("show", f"{sha}:{path}", check=False)
        if cp.returncode != 0:
            return None
        return cp.stdout


@lru_cache(maxsize=None)
def count_cosmic_sights_text(text: str | None) -> int | None:
    """Count top-level object literals in const cosmicSights = [...].

    This is a lightweight source scanner, not a general JavaScript parser. It is
    intentionally conservative: if the array start/end cannot be found, return
    None. It ignores braces inside quoted strings and comments well enough for
    the observed one-line cosmic sight object style.
    """
    if text is None:
        return None
    start = text.find("const cosmicSights = [")
    if start < 0:
        return None
    i = text.find("[", start)
    if i < 0:
        return None
    depth = 0
    in_str = None
    escape = False
    line_comment = False
    block_comment = False
    top_objects = 0
    object_depth = 0
    j = i
    while j < len(text):
        ch = text[j]
        nxt = text[j + 1] if j + 1 < len(text) else ""
        if line_comment:
            if ch == "\n":
                line_comment = False
            j += 1
            continue
        if block_comment:
            if ch == "*" and nxt == "/":
                block_comment = False
                j += 2
            else:
                j += 1
            continue
        if in_str:
            if escape:
                escape = False
            elif ch == "\\":
                escape = True
            elif ch == in_str:
                in_str = None
            j += 1
            continue
        if ch in "'\"`":
            in_str = ch
            j += 1
            continue
        if ch == "/" and nxt == "/":
            line_comment = True
            j += 2
            continue
        if ch == "/" and nxt == "*":
            block_comment = True
            j += 2
            continue
        if ch == "[":
            depth += 1
        elif ch == "]":
            depth -= 1
            if depth == 0:
                return top_objects
        elif ch == "{" and depth == 1:
            if object_depth == 0:
                top_objects += 1
            object_depth += 1
        elif ch == "}" and depth == 1 and object_depth > 0:
            object_depth -= 1
        j += 1
    return None


def touch_flags(names: list[str]) -> dict[str, int]:
    return {
        "git_touch_main_js": int("main.js" in names),
        "git_touch_config_js": int("config.js" in names),
        "git_touch_anchorage": int(any(n == "landmarks/anchorage.js" for n in names)),
        "git_touch_landmark": int(any(n.startswith("landmarks/") for n in names)),
        "git_touch_validator": int(any("validator" in n.lower() or n.startswith("scripts/") for n in names)),
    }


def status_counts(statuses: list[str]) -> dict[str, int]:
    return {
        "git_added_files": sum(1 for s in statuses if s.startswith("A")),
        "git_modified_files": sum(1 for s in statuses if s.startswith("M")),
        "git_removed_files": sum(1 for s in statuses if s.startswith("D")),
        "git_renamed_or_copied_files": sum(1 for s in statuses if s.startswith(("R", "C"))),
    }


def build_metrics(repo: Path, count_cosmic: bool = False) -> list[dict[str, object]]:
    git = Git(repo)
    rows = []
    raw = load_jsonl(DATA / "raw_prs.jsonl")
    for pr in sorted(raw, key=lambda r: int(r["number"])):
        number = int(pr["number"])
        base = pr.get("base_sha") or ""
        head = pr.get("head_sha") or ""
        merge_sha = pr.get("merge_commit_sha") or ""
        base_exists = git.exists(base)
        head_exists = git.exists(head)
        merge_exists = git.exists(merge_sha)
        rec: dict[str, object] = {
            "number": number,
            "git_base_exists": int(base_exists),
            "git_head_exists": int(head_exists),
            "git_merge_sha_exists": int(merge_exists),
        }
        if base_exists and head_exists:
            behind, ahead = git.rev_counts(base, head)
            mb = git.merge_base(base, head)
            rec.update({
                "git_merge_base_sha": mb,
                "git_base_is_ancestor_of_head": int(bool(git.is_ancestor(base, head))),
                "git_merge_base_is_base": int(mb == base),
                "git_commits_behind_base": behind,
                "git_commits_ahead_base": ahead,
            })
            files_changed, additions, deletions = git.diff_numstat(base, head)
            name_status = list(git.diff_name_status(base, head))
            statuses = [s for s, _ in name_status]
            names = [n for _, n in name_status]
            rec.update({
                "git_files_changed": files_changed,
                "git_additions": additions,
                "git_deletions": deletions,
                "git_changes": additions + deletions,
                "git_deletion_ratio": deletions / max(additions + deletions, 1),
                "git_filenames": ";".join(names),
            })
            rec.update(touch_flags(names))
            rec.update(status_counts(statuses))
            if count_cosmic and "main.js" in names:
                base_count = count_cosmic_sights_text(git.show_file(base, "main.js"))
                head_count = count_cosmic_sights_text(git.show_file(head, "main.js"))
            else:
                base_count = head_count = None
            rec.update({
                "git_base_cosmic_sights": base_count,
                "git_head_cosmic_sights": head_count,
                "git_cosmic_sights_delta": (head_count - base_count) if base_count is not None and head_count is not None else None,
            })
        rows.append(rec)
    return rows


def write_csv(rows: list[dict[str, object]], path: Path) -> None:
    fieldnames = []
    seen = set()
    for row in rows:
        for k in row:
            if k not in seen:
                seen.add(k)
                fieldnames.append(k)
    with path.open("w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=fieldnames)
        w.writeheader()
        for row in rows:
            w.writerow(row)


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--universe-repo", type=Path, default=DEFAULT_UNIVERSE, help="Local ai-village-agents/the-universe clone")
    ap.add_argument("--output", type=Path, default=RESULTS / "git_pr_metrics.csv")
    ap.add_argument("--count-cosmic", action="store_true", help="Also parse main.js cosmicSights counts for PRs touching main.js (slower)")
    args = ap.parse_args()
    if not (args.universe_repo / ".git").exists():
        print(f"Universe repo not found at {args.universe_repo}; set --universe-repo or UNIVERSE_REPO", file=sys.stderr)
        return 2
    rows = build_metrics(args.universe_repo, count_cosmic=args.count_cosmic)
    write_csv(rows, args.output)
    print(f"Wrote {args.output} ({len(rows)} PRs)")
    base_ok = sum(int(r.get("git_base_exists", 0)) for r in rows)
    head_ok = sum(int(r.get("git_head_exists", 0)) for r in rows)
    merge_ok = sum(int(r.get("git_merge_sha_exists", 0)) for r in rows)
    print(f"commit availability: base={base_ok}/{len(rows)} head={head_ok}/{len(rows)} merge_sha={merge_ok}/{len(rows)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
