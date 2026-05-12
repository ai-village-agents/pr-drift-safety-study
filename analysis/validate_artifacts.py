#!/usr/bin/env python3
"""Validate published PR-drift study artifacts.

This is a lightweight structural validator: it checks row counts, required
columns, simple key uniqueness, and relative Markdown links. It does not treat
weak keyword labels as ground truth or adjudicate PR safety.
"""
from __future__ import annotations

import csv
import json
import re
import sys
import urllib.parse
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

EXPECTED_JSONL_ROWS = {
    "data/raw_prs.jsonl": 610,
    "data/pr_files.jsonl": 610,
    "data/pr_comments.jsonl": 610,
}

EXPECTED_CSV_ROWS = {
    "results/pr_level_features.csv": 610,
    "results/git_pr_metrics.csv": 610,
    "results/manual_validation_sample.csv": 79,
    "results/manual_validation_template.csv": 79,
    "results/manual_validation_pilot.csv": 11,
}

REQUIRED_COLUMNS = {
    "results/pr_level_features.csv": {
        "number", "title", "user", "state", "merged", "closed_unmerged",
        "risk_comment_label", "touch_main_js", "touch_landmark",
        "kw_stale", "kw_rollback", "kw_duplicate",
    },
    "results/git_pr_metrics.csv": {
        "number", "git_base_exists", "git_head_exists", "git_merge_sha_exists",
        "git_base_is_ancestor_of_head", "git_commits_behind_base",
        "git_deletions", "git_touch_main_js", "git_touch_landmark",
    },
    "results/manual_validation_sample.csv": {
        "validation_stratum", "number", "title", "user", "state", "merged",
        "closed_unmerged", "risk_comment_label", "html_url",
    },
    "results/manual_validation_template.csv": {
        "validation_stratum", "number", "title", "user", "state", "merged",
        "closed_unmerged", "risk_comment_label", "html_url",
        "manual_rollback_risk", "manual_source_integrity_risk",
        "manual_duplicate_or_superseded", "manual_label_confidence", "manual_notes",
    },
    "results/manual_validation_pilot.csv": {
        "validation_stratum", "number", "title", "user", "state", "merged",
        "closed_unmerged", "risk_comment_label", "html_url", "git_deletions",
        "git_commits_behind_base", "git_base_is_ancestor_of_head",
        "manual_rollback_risk", "manual_source_integrity_risk",
        "manual_duplicate_or_superseded", "manual_label_confidence", "manual_notes",
    },
}

REQUIRED_REPORTS = [
    "README.md",
    "DATA_CARD.md",
    "docs/preregistration.md",
    "docs/case_studies.md",
    "docs/manual_validation_protocol.md",
    "results/descriptive_report.md",
    "results/gemini_model_analysis.md",
    "results/model_outcomes.md",
    "results/manual_validation_sample.md",
    "results/manual_validation_pilot.md",
]


def fail(msg: str) -> None:
    print(f"ERROR: {msg}", file=sys.stderr)
    raise SystemExit(1)


def read_jsonl(path: Path) -> list[dict]:
    rows = []
    with path.open() as f:
        for i, line in enumerate(f, 1):
            if not line.strip():
                continue
            try:
                obj = json.loads(line)
            except json.JSONDecodeError as e:
                fail(f"{path}: line {i} is not valid JSON: {e}")
            if not isinstance(obj, dict):
                fail(f"{path}: line {i} is not a JSON object")
            rows.append(obj)
    return rows


def read_csv(path: Path) -> list[dict]:
    with path.open(newline="") as f:
        return list(csv.DictReader(f))


def require_unique_numbers(rows: list[dict], rel: str) -> None:
    nums = [str(r.get("number", "")) for r in rows]
    if any(not n for n in nums):
        fail(f"{rel}: missing number values")
    if len(set(nums)) != len(nums):
        fail(f"{rel}: number values are not unique")


def check_jsonl() -> None:
    for rel, expected in EXPECTED_JSONL_ROWS.items():
        path = ROOT / rel
        if not path.exists():
            fail(f"missing {rel}")
        rows = read_jsonl(path)
        if len(rows) != expected:
            fail(f"{rel}: expected {expected} rows, found {len(rows)}")
        require_unique_numbers(rows, rel)
        print(f"OK {rel}: {len(rows)} rows")


def check_csvs() -> None:
    for rel, expected in EXPECTED_CSV_ROWS.items():
        path = ROOT / rel
        if not path.exists():
            fail(f"missing {rel}")
        rows = read_csv(path)
        if len(rows) != expected:
            fail(f"{rel}: expected {expected} rows, found {len(rows)}")
        header = set(rows[0].keys() if rows else [])
        missing = sorted(REQUIRED_COLUMNS.get(rel, set()) - header)
        if missing:
            fail(f"{rel}: missing required columns {missing}")
        require_unique_numbers(rows, rel)
        print(f"OK {rel}: {len(rows)} rows, {len(header)} columns")

    features = read_csv(ROOT / "results/pr_level_features.csv")
    merged = sum(int(float(r["merged"])) for r in features)
    closed = sum(int(float(r["closed_unmerged"])) for r in features)
    open_ = sum(int(float(r.get("open", "0") or 0)) for r in features)
    if (merged, closed, open_) != (356, 253, 1):
        fail(f"feature outcome counts changed: merged={merged}, closed={closed}, open={open_}")
    risk = sum(int(float(r["risk_comment_label"])) for r in features)
    if risk != 124:
        fail(f"risk_comment_label count changed: {risk}")
    print("OK results/pr_level_features.csv: outcome/risk counts match report")

    git_rows = read_csv(ROOT / "results/git_pr_metrics.csv")
    base = sum(r["git_base_exists"] == "1" for r in git_rows)
    head = sum(r["git_head_exists"] == "1" for r in git_rows)
    merge_sha = sum(r["git_merge_sha_exists"] == "1" for r in git_rows)
    non_desc = sum(r["git_base_is_ancestor_of_head"] == "0" for r in git_rows)
    if (base, head, merge_sha, non_desc) != (610, 610, 356, 144):
        fail(
            "git metric counts changed: "
            f"base={base}, head={head}, merge_sha={merge_sha}, non_desc={non_desc}"
        )
    print("OK results/git_pr_metrics.csv: availability/stale counts match report")


def check_reports_exist() -> None:
    for rel in REQUIRED_REPORTS:
        path = ROOT / rel
        if not path.exists():
            fail(f"missing report/doc {rel}")
        if path.stat().st_size == 0:
            fail(f"empty report/doc {rel}")
        print(f"OK {rel}: present")


def check_markdown_links() -> None:
    missing = []
    checked = 0
    for md in sorted(ROOT.rglob("*.md")):
        if any(part in {".git", "node_modules", "__pycache__"} for part in md.parts):
            continue
        text = md.read_text(errors="replace")
        for m in re.finditer(r"!?(?<!\\)\[[^\]]*\]\(([^)]+)\)", text):
            target = m.group(1).strip()
            if target.startswith(("http://", "https://", "mailto:")):
                continue
            target = target.split("#", 1)[0].strip()
            if not target:
                continue
            target = urllib.parse.unquote(target)
            p = (md.parent / target).resolve()
            try:
                rel = p.relative_to(ROOT)
            except ValueError:
                missing.append((str(md.relative_to(ROOT)), target, "outside repo"))
                continue
            checked += 1
            if not (ROOT / rel).exists():
                missing.append((str(md.relative_to(ROOT)), target, f"missing {rel}"))
    if missing:
        for item in missing:
            print(item, file=sys.stderr)
        fail(f"{len(missing)} Markdown link targets are missing")
    print(f"OK Markdown relative links: {checked} checked")


def main() -> None:
    check_jsonl()
    check_csvs()
    check_reports_exist()
    check_markdown_links()
    print("All published PR-drift artifacts passed structural validation.")


if __name__ == "__main__":
    main()
