#!/usr/bin/env python3
"""Analyze PR-level safety signals in the AI Village Universe sprint.

This script intentionally uses only the Python standard library plus pandas/numpy
so it can run in the same minimal environment as the main research project.
"""
from __future__ import annotations

import json
import math
import re
from collections import Counter, defaultdict
from datetime import datetime, timezone
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data"
RESULTS = ROOT / "results"
RESULTS.mkdir(exist_ok=True)

KEYWORDS = {
    "stale": r"\bstale\b|out of date|behind|rebase|far out of date",
    "rollback": r"rollback|delete[s]? .*current|delete[s]? .*tail|replacement-risk|replace[s]? recently|would delete",
    "sparse": r"sparse array|hole[s]?|empty slot",
    "post_array": r"post-array|after .*array|after .*cosmicSights|outside .*array",
    "duplicate": r"duplicate|superseded|replaced by|replacement PR",
    "green_but_bad": r"green check|checks? (?:are )?green|CI.*green|green CI|checks? pass|CI passes|even if CI passes|mechanically mergeable",
    "not_merge_safe": r"not merge-safe|no longer merge-safe|isn['’]?t merge-safe|not safe to merge|unsafe to merge",
    "merge_safe_positive": r"(?<!not )(?<!longer )merge-safe|safe to merge|clean append|minimal diff",
}
RISK_KEYS = ["stale", "rollback", "sparse", "post_array", "duplicate", "green_but_bad", "not_merge_safe"]


def load_jsonl(path: Path):
    return [json.loads(line) for line in path.read_text().splitlines() if line.strip()]


def parse_dt(s):
    if not s:
        return pd.NaT
    return pd.to_datetime(s, utc=True)


def file_features(files):
    additions = sum((f.get("additions") or 0) for f in files)
    deletions = sum((f.get("deletions") or 0) for f in files)
    changes = sum((f.get("changes") or 0) for f in files)
    names = [f.get("filename") or "" for f in files]
    statuses = Counter(f.get("status") or "" for f in files)
    return {
        "files_changed": len(files),
        "additions": additions,
        "deletions": deletions,
        "changes": changes,
        "deletion_ratio": deletions / max(additions + deletions, 1),
        "touch_main_js": int("main.js" in names),
        "touch_config_js": int("config.js" in names),
        "touch_anchorage": int(any(n == "landmarks/anchorage.js" for n in names)),
        "touch_landmark": int(any(n.startswith("landmarks/") for n in names)),
        "touch_validator": int(any("validator" in n.lower() or n.startswith("scripts/") for n in names)),
        "added_files": statuses.get("added", 0),
        "modified_files": statuses.get("modified", 0),
        "removed_files": statuses.get("removed", 0),
        "filenames": ";".join(names),
    }


def comment_features(comments):
    body = "\n".join((c.get("body") or "") for c in comments)
    low = body.lower()
    out = {f"kw_{k}": int(re.search(pat, low, flags=re.I | re.S) is not None) for k, pat in KEYWORDS.items()}
    out["comment_count"] = len(comments)
    out["comment_chars"] = len(body)
    out["risk_comment_label"] = int(any(out[f"kw_{k}"] for k in RISK_KEYS))
    return out


def title_features(title):
    low = (title or "").lower()
    m = re.search(r"(\d{3,6})\s*[-–]\s*(\d{3,6})", low)
    if m:
        lo, hi = int(m.group(1)), int(m.group(2))
        span = hi - lo + 1 if hi >= lo else np.nan
    else:
        lo = hi = span = np.nan
    return {
        "title_cosmic_batch": int("batch" in low or "cosmic" in low or "sight" in low),
        "title_landmark": int("anchorage" in low or "landmark" in low or "world" in low),
        "title_fix": int("fix" in low or "guard" in low or "validator" in low),
        "slot_start": lo,
        "slot_end": hi,
        "slot_span": span,
    }


def make_frame():
    raw = {r["number"]: r for r in load_jsonl(DATA / "raw_prs.jsonl")}
    files = {r["number"]: r["files"] for r in load_jsonl(DATA / "pr_files.jsonl")}
    comments = {r["number"]: r["comments"] for r in load_jsonl(DATA / "pr_comments.jsonl")}
    recs = []
    for n in sorted(raw):
        pr = raw[n]
        rec = dict(pr)
        rec.update(file_features(files.get(n, [])))
        rec.update(comment_features(comments.get(n, [])))
        rec.update(title_features(pr.get("title") or ""))
        rec["merged"] = int(bool(pr.get("merged_at")))
        rec["closed_unmerged"] = int(pr.get("state") == "closed" and not pr.get("merged_at"))
        rec["open"] = int(pr.get("state") == "open")
        recs.append(rec)
    df = pd.DataFrame(recs)
    for c in ["created_at", "updated_at", "closed_at", "merged_at"]:
        df[c] = df[c].map(parse_dt)
    df = df.sort_values("created_at").reset_index(drop=True)
    df["created_hour_utc"] = df["created_at"].dt.hour
    df["created_date"] = df["created_at"].dt.date.astype(str)
    merged_times = sorted(t for t in df["merged_at"].dropna())
    since_prev = []
    merges_prior_30m = []
    open_prior_30m = []
    for _, row in df.iterrows():
        t = row["created_at"]
        prev = [m for m in merged_times if m < t]
        since_prev.append((t - prev[-1]).total_seconds() / 60 if prev else np.nan)
        merges_prior_30m.append(sum(1 for m in merged_times if pd.Timedelta(0) <= t - m <= pd.Timedelta(minutes=30)))
        t0 = t - pd.Timedelta(minutes=30)
        open_prior_30m.append(int(((df["created_at"] >= t0) & (df["created_at"] < t)).sum()))
    df["minutes_since_prev_merge"] = since_prev
    df["merges_prior_30m"] = merges_prior_30m
    df["prs_created_prior_30m"] = open_prior_30m

    git_metrics_path = RESULTS / "git_pr_metrics.csv"
    if git_metrics_path.exists():
        git_df = pd.read_csv(git_metrics_path)
        # Keep generated feature CSV one-row-per-PR while preserving API and git
        # fields separately.  Git fields are prefixed `git_`.
        df = df.merge(git_df, on="number", how="left", validate="one_to_one")
        for c in [
            "git_base_exists", "git_head_exists", "git_merge_sha_exists",
            "git_base_is_ancestor_of_head", "git_merge_base_is_base",
            "git_touch_main_js", "git_touch_config_js", "git_touch_anchorage",
            "git_touch_landmark", "git_touch_validator",
        ]:
            if c in df:
                df[c] = df[c].fillna(0).astype(int)
    return df


def markdown_table(df, cols=None, max_rows=None, floatfmt=".3f"):
    if cols:
        df = df[cols]
    if max_rows:
        df = df.head(max_rows)
    if df.empty:
        return "_(none)_"
    d = df.copy()
    for col in d.columns:
        if pd.api.types.is_float_dtype(d[col]):
            d[col] = d[col].map(lambda x: "" if pd.isna(x) else format(x, floatfmt))
    return d.to_markdown(index=False)


def rate_table(df, by):
    g = df.groupby(by, dropna=False).agg(
        prs=("number", "count"),
        merged=("merged", "sum"),
        closed_unmerged=("closed_unmerged", "sum"),
        open=("open", "sum"),
        risk_comments=("risk_comment_label", "sum"),
        mean_deletions=("deletions", "mean"),
        median_deletions=("deletions", "median"),
        main_js_rate=("touch_main_js", "mean"),
    ).reset_index()
    g["merge_rate"] = g["merged"] / g["prs"]
    g["risk_comment_rate"] = g["risk_comments"] / g["prs"]
    return g.sort_values(["risk_comment_rate", "prs"], ascending=[False, False])


def simple_feature_screen(df, features, target):
    rows = []
    for f in features:
        x = df[f]
        y = df[target]
        if x.nunique(dropna=True) <= 1 or y.nunique(dropna=True) <= 1:
            continue
        if set(x.dropna().unique()).issubset({0, 1}):
            a = df.loc[x == 1, target]
            b = df.loc[x == 0, target]
            rows.append({
                "feature": f,
                "kind": "binary",
                "n_feature": int((x == 1).sum()),
                "target_rate_if_feature": a.mean() if len(a) else np.nan,
                "target_rate_if_absent": b.mean() if len(b) else np.nan,
                "difference": (a.mean() - b.mean()) if len(a) and len(b) else np.nan,
                "corr": np.corrcoef(x.fillna(0), y)[0, 1],
            })
        else:
            xx = x.astype(float)
            ok = xx.notna() & y.notna()
            if ok.sum() >= 5 and xx[ok].std() > 0:
                rows.append({
                    "feature": f,
                    "kind": "numeric",
                    "n_feature": int(ok.sum()),
                    "target_rate_if_feature": np.nan,
                    "target_rate_if_absent": np.nan,
                    "difference": np.nan,
                    "corr": np.corrcoef(xx[ok], y[ok])[0, 1],
                })
    out = pd.DataFrame(rows)
    if not out.empty:
        out["abs_corr"] = out["corr"].abs()
        out = out.sort_values("abs_corr", ascending=False).drop(columns=["abs_corr"])
    return out


def main():
    df = make_frame()
    out_csv = RESULTS / "pr_level_features.csv"
    df.to_csv(out_csv, index=False)

    features = [
        "files_changed", "additions", "deletions", "changes", "deletion_ratio",
        "touch_main_js", "touch_config_js", "touch_anchorage", "touch_landmark", "touch_validator",
        "added_files", "modified_files", "removed_files", "comment_count", "comment_chars",
        "title_cosmic_batch", "title_landmark", "title_fix", "slot_span",
        "minutes_since_prev_merge", "merges_prior_30m", "prs_created_prior_30m",
    ] + [f"kw_{k}" for k in KEYWORDS]
    if "git_deletions" in df.columns:
        features += [
            "git_commits_ahead_base", "git_commits_behind_base", "git_files_changed",
            "git_additions", "git_deletions", "git_deletion_ratio",
            "git_base_is_ancestor_of_head", "git_merge_base_is_base",
            "git_touch_main_js", "git_touch_landmark", "git_touch_anchorage", "git_touch_validator",
        ]

    overall = pd.DataFrame([{
        "PRs": len(df),
        "merged": int(df["merged"].sum()),
        "closed_unmerged": int(df["closed_unmerged"].sum()),
        "open": int(df["open"].sum()),
        "merge_rate": df["merged"].mean(),
        "risk_comment_labels": int(df["risk_comment_label"].sum()),
        "risk_comment_rate": df["risk_comment_label"].mean(),
        "touch_main_js_rate": df["touch_main_js"].mean(),
    }])
    by_author = rate_table(df, "user")
    by_date = rate_table(df, "created_date").sort_values("created_date")
    file_touch = pd.DataFrame([
        {"signal": s, "prs": int(df[s].sum()), "merge_rate": df.loc[df[s] == 1, "merged"].mean(), "risk_comment_rate": df.loc[df[s] == 1, "risk_comment_label"].mean()}
        for s in ["touch_main_js", "touch_landmark", "touch_anchorage", "touch_validator", "title_cosmic_batch", "title_landmark", "title_fix"]
    ])
    keyword_counts = pd.DataFrame([
        {"keyword_label": k, "prs": int(df[f"kw_{k}"].sum()), "merge_rate": df.loc[df[f"kw_{k}"] == 1, "merged"].mean() if df[f"kw_{k}"].sum() else np.nan}
        for k in KEYWORDS
    ]).sort_values("prs", ascending=False)
    screen_merge = simple_feature_screen(df, features, "merged").head(15)
    screen_risk = simple_feature_screen(df, features, "risk_comment_label").head(15)
    risk_examples = df[df["risk_comment_label"] == 1].sort_values(["kw_rollback", "kw_stale", "deletions"], ascending=False).head(12)
    deletion_examples = df.sort_values("deletions", ascending=False).head(12)
    have_git = "git_deletions" in df.columns
    if have_git:
        git_overall = pd.DataFrame([{
            "PRs_with_git_metrics": int(df["git_head_exists"].notna().sum()),
            "base_commits_available": int(df["git_base_exists"].sum()),
            "head_commits_available": int(df["git_head_exists"].sum()),
            "merge_shas_available": int(df["git_merge_sha_exists"].sum()),
            "head_not_descendant_of_base": int((df["git_base_is_ancestor_of_head"] == 0).sum()),
            "mean_git_deletions": df["git_deletions"].mean(),
            "median_git_deletions": df["git_deletions"].median(),
            "max_git_deletions": df["git_deletions"].max(),
        }])
        git_desc = pd.DataFrame([{
            "metric": c,
            "mean": df[c].mean(),
            "median": df[c].median(),
            "p90": df[c].quantile(0.90),
            "max": df[c].max(),
        } for c in ["git_commits_ahead_base", "git_commits_behind_base", "git_files_changed", "git_additions", "git_deletions"]])
        stale_git = df[df["git_base_is_ancestor_of_head"] == 0].sort_values("git_deletions", ascending=False).head(12)
        git_deletion_examples = df.sort_values("git_deletions", ascending=False).head(12)
        compare_cols = [
            "touch_main_js", "git_touch_main_js", "touch_landmark", "git_touch_landmark",
            "files_changed", "git_files_changed", "additions", "git_additions", "deletions", "git_deletions",
        ]
        touch_mismatch = pd.DataFrame([{
            "comparison": "main.js touch API vs git",
            "mismatches": int((df["touch_main_js"] != df["git_touch_main_js"]).sum()),
        }, {
            "comparison": "landmark touch API vs git",
            "mismatches": int((df["touch_landmark"] != df["git_touch_landmark"]).sum()),
        }, {
            "comparison": "API deletion count differs from git",
            "mismatches": int((df["deletions"] != df["git_deletions"]).sum()),
        }])

    report = []
    report.append("# PR Drift Safety Study: descriptive analysis\n")
    report.append("This is a first-pass descriptive analysis of GitHub PR metadata, changed-file summaries, and issue comments from `ai-village-agents/the-universe`. Risk labels are keyword-derived from PR comments, not final manual adjudications.\n")
    report.append("## Coverage\n")
    report.append(markdown_table(overall))
    report.append("\n## PR volume by creation date\n")
    report.append(markdown_table(by_date[["created_date", "prs", "merged", "closed_unmerged", "open", "merge_rate", "risk_comment_rate", "mean_deletions"]]))
    report.append("\n## File/topic touch signals\n")
    report.append(markdown_table(file_touch))
    if have_git:
        report.append("\n## Git-derived base/head diff metrics\n")
        report.append("These metrics are computed locally with `git diff base_sha..head_sha` after fetching all PR heads. They are independent of GitHub API file summaries and capture stale-branch two-dot diffs that can delete already-current content. They are still syntactic triage signals, not semantic safety labels.\n")
        report.append(markdown_table(git_overall))
        report.append("\n### Git metric distributions\n")
        report.append(markdown_table(git_desc))
        report.append("\n### API vs local-git agreement checks\n")
        report.append(markdown_table(touch_mismatch))
        report.append("\n### Largest git two-dot deletion PRs\n")
        report.append(markdown_table(git_deletion_examples[["number", "title", "user", "merged", "closed_unmerged", "git_commits_behind_base", "git_commits_ahead_base", "git_files_changed", "git_additions", "git_deletions", "git_touch_main_js", "git_touch_landmark", "risk_comment_label"]]))
        report.append("\n### Largest deletion PRs where head is not a descendant of base\n")
        report.append(markdown_table(stale_git[["number", "title", "user", "merged", "closed_unmerged", "git_commits_behind_base", "git_files_changed", "git_additions", "git_deletions", "risk_comment_label"]]))
    report.append("\n## Comment keyword labels\n")
    report.append(markdown_table(keyword_counts))
    report.append("\n## Authors with at least 10 PRs\n")
    auth = by_author[by_author["prs"] >= 10].sort_values("prs", ascending=False)
    report.append(markdown_table(auth[["user", "prs", "merged", "closed_unmerged", "open", "merge_rate", "risk_comment_rate", "main_js_rate", "mean_deletions"]]))
    report.append("\n## Feature screen: association with merge outcome\n")
    report.append(markdown_table(screen_merge[["feature", "kind", "n_feature", "target_rate_if_feature", "target_rate_if_absent", "difference", "corr"]]))
    report.append("\n## Feature screen: association with keyword risk comments\n")
    report.append(markdown_table(screen_risk[["feature", "kind", "n_feature", "target_rate_if_feature", "target_rate_if_absent", "difference", "corr"]]))
    report.append("\n## Highest-deletion PRs\n")
    report.append(markdown_table(deletion_examples[["number", "title", "user", "merged", "closed_unmerged", "deletions", "additions", "files_changed", "touch_main_js", "risk_comment_label"]]))
    report.append("\n## Keyword-risk examples\n")
    report.append(markdown_table(risk_examples[["number", "title", "user", "merged", "closed_unmerged", "deletions", "additions", "kw_stale", "kw_rollback", "kw_sparse", "kw_post_array", "kw_duplicate", "kw_green_but_bad"]]))
    report.append("\n## Provisional takeaways\n")
    report.append("- The dataset is now complete for PR metadata, file summaries, and issue comments.\n")
    report.append("- Keyword labels are useful for triage but should be treated as weak supervision; the next step is manual validation of a stratified sample, especially high-deletion and stale/rollback-commented PRs.\n")
    report.append("- Deletion-heavy diffs, `main.js` touches, and queue-density features are available for testing the preregistered stale/rollback-risk hypotheses.\n")
    if have_git:
        report.append("- Local git metrics sharpen the stale-branch picture: every PR base/head commit was recoverable, but 144 PR heads were not descendants of their recorded base and some two-dot diffs implied tens of thousands of deletions. These are triage flags, not automatic failure labels.\n")

    report_path = RESULTS / "descriptive_report.md"
    report_path.write_text("\n".join(report))
    print(f"Wrote {out_csv}")
    print(f"Wrote {report_path}")
    print(markdown_table(overall))


if __name__ == "__main__":
    main()
