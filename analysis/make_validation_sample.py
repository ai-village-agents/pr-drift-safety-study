#!/usr/bin/env python3
"""Create a deterministic stratified sample for manual PR-drift label validation.

The descriptive analysis uses comment-keyword labels as weak supervision.  This
script chooses PRs for later manual adjudication from strata that should expose
both true positives and likely false positives/negatives.
"""
from __future__ import annotations

from pathlib import Path
import hashlib
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
FEATURES = ROOT / "results" / "pr_level_features.csv"
OUT_CSV = ROOT / "results" / "manual_validation_sample.csv"
OUT_MD = ROOT / "results" / "manual_validation_sample.md"


def stable_rank(number: int, salt: str) -> int:
    digest = hashlib.sha256(f"{salt}:{number}".encode()).hexdigest()
    return int(digest[:16], 16)


def pick(df: pd.DataFrame, mask, n: int, stratum: str, selected: set[int]) -> pd.DataFrame:
    cand = df.loc[mask].copy()
    cand = cand[~cand["number"].isin(selected)].copy()
    if cand.empty:
        return cand.assign(validation_stratum=stratum)
    cand["_rank"] = cand["number"].map(lambda x: stable_rank(int(x), stratum))
    cand = cand.sort_values(["_rank", "number"]).head(n).drop(columns=["_rank"])
    selected.update(int(x) for x in cand["number"])
    cand["validation_stratum"] = stratum
    return cand


def main() -> None:
    df = pd.read_csv(FEATURES)
    selected: set[int] = set()
    strata = [
        ("keyword_risk_positive", df["risk_comment_label"].eq(1), 20),
        ("keyword_risk_negative_main_js", df["risk_comment_label"].eq(0) & df["touch_main_js"].eq(1), 15),
        ("high_deletion_no_keyword", df["risk_comment_label"].eq(0) & df["deletions"].ge(25), 10),
        ("merged_high_deletion", df["merged"].eq(1) & df["deletions"].ge(25), 8),
        ("landmark_or_anchorage", (df["touch_landmark"].eq(1) | df["touch_anchorage"].eq(1)), 12),
        ("closed_no_keyword", df["closed_unmerged"].eq(1) & df["risk_comment_label"].eq(0), 12),
        ("green_but_bad_keyword", df.get("kw_green_but_bad", pd.Series(0, index=df.index)).eq(1), 5),
        ("post_array_or_sparse", df.get("kw_post_array", pd.Series(0, index=df.index)).eq(1) | df.get("kw_sparse", pd.Series(0, index=df.index)).eq(1), 8),
    ]
    pieces = [pick(df, mask, n, name, selected) for name, mask, n in strata]
    sample = pd.concat([p for p in pieces if not p.empty], ignore_index=True)
    cols = [
        "validation_stratum", "number", "title", "user", "state", "merged",
        "closed_unmerged", "risk_comment_label", "deletions", "additions",
        "files_changed", "touch_main_js", "touch_landmark", "touch_anchorage",
        "comment_count", "kw_stale", "kw_rollback", "kw_duplicate",
        "kw_post_array", "kw_sparse", "kw_green_but_bad", "html_url",
    ]
    cols = [c for c in cols if c in sample.columns]
    sample = sample[cols].sort_values(["validation_stratum", "number"])
    sample.to_csv(OUT_CSV, index=False)

    counts = sample.groupby("validation_stratum").size().reset_index(name="n")
    lines = [
        "# Manual validation sample",
        "",
        "Deterministic stratified sample for auditing weak PR-risk labels in the PR Drift Safety Study.",
        "The intended manual fields are: `manual_rollback_risk`, `manual_source_integrity_risk`, `manual_duplicate_or_superseded`, and `notes`.",
        "",
        "## Stratum counts",
        "",
        counts.to_markdown(index=False),
        "",
        "## Sample",
        "",
        sample.to_markdown(index=False),
        "",
    ]
    OUT_MD.write_text("\n".join(lines))
    print(f"Wrote {len(sample)} PRs to {OUT_CSV}")
    print(f"Wrote Markdown report to {OUT_MD}")


if __name__ == "__main__":
    main()
