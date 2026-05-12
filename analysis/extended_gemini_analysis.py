#!/usr/bin/env python3
"""Extended heuristic analysis of PR-drift predictors.

Originally proposed by Gemini 3.1 Pro as a lightweight, no-scikit-learn extension
of the PR drift study. This version keeps the analysis descriptive and updates it
to work with the current feature table, including optional git-derived metrics.
"""
from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
RESULTS = ROOT / "results"
OUT_REPORT = RESULTS / "gemini_model_analysis.md"


def pct(x: float) -> str:
    return "" if pd.isna(x) else f"{x:.1%}"


def categorical_block(df: pd.DataFrame, features: list[str]) -> list[str]:
    report = ["## Likelihood of merge by categorical feature\n"]
    for f in features:
        if f not in df.columns:
            continue
        present = df[df[f] == 1]
        absent = df[df[f] == 0]
        rate_present = present["merged"].mean()
        rate_absent = absent["merged"].mean()
        report.extend([
            f"**{f}**:\n",
            f"- Present: {pct(rate_present)} merged (n={len(present)})\n",
            f"- Absent: {pct(rate_absent)} merged (n={len(absent)})\n",
            f"- Difference: {rate_present - rate_absent:+.1%}\n\n",
        ])
    return report


def deletion_threshold_block(df: pd.DataFrame, col: str, thresholds: list[int]) -> list[str]:
    label = "Git two-dot deletions" if col.startswith("git_") else "GitHub API deletions"
    report = [f"## {label}: merge rates above simple thresholds\n"]
    if col not in df.columns:
        report.append(f"_{col} not present in feature table._\n")
        return report
    for thresh in thresholds:
        high = df[df[col] > thresh]
        low = df[df[col] <= thresh]
        report.extend([
            f"**{col} > {thresh}**:\n",
            f"- > {thresh}: {pct(high['merged'].mean())} merged (n={len(high)})\n",
            f"- <= {thresh}: {pct(low['merged'].mean())} merged (n={len(low)})\n\n",
        ])
    return report


def main() -> None:
    df = pd.read_csv(RESULTS / "pr_level_features.csv")
    df = df[df["open"] == 0].copy()

    features = [
        "touch_main_js", "touch_anchorage", "title_cosmic_batch",
        "touch_config_js", "touch_landmark",
    ]
    if "git_base_is_ancestor_of_head" in df.columns:
        df["git_head_not_descendant_of_base"] = 1 - df["git_base_is_ancestor_of_head"]
        features += ["git_head_not_descendant_of_base", "git_touch_main_js", "git_touch_landmark"]

    report: list[str] = []
    report.append("# Extended Gemini 3.1 Pro Analysis: heuristic predictors of PR success\n")
    report.append("This is a lightweight descriptive extension of the PR drift study, calculated without scikit-learn. It reports simple marginal merge rates, not a causal model and not manual safety adjudication.\n")
    report += categorical_block(df, features)
    report += deletion_threshold_block(df, "deletions", [0, 5, 10, 50, 100])
    if "git_deletions" in df.columns:
        report += deletion_threshold_block(df, "git_deletions", [0, 10, 100, 1000, 10000])

    if "git_commits_behind_base" in df.columns:
        report.append("## Stale-distance bins from local git\n")
        bins = [(-np.inf, 0, "0 commits behind"), (0, 1, "1 commit behind"), (1, 5, "2-5 commits behind"), (5, 50, "6-50 commits behind"), (50, np.inf, ">50 commits behind")]
        for lo, hi, label in bins:
            if np.isneginf(lo):
                part = df[df["git_commits_behind_base"] <= hi]
            elif np.isposinf(hi):
                part = df[df["git_commits_behind_base"] > lo]
            else:
                part = df[(df["git_commits_behind_base"] > lo) & (df["git_commits_behind_base"] <= hi)]
            report.append(f"- {label}: {pct(part['merged'].mean())} merged (n={len(part)})\n")
        report.append("\n")

    report.append("## Takeaways\n")
    report.append("- PRs touching `main.js` or having cosmic-batch titles were much less likely to merge in this trace, while landmark/Anchorage PRs had much higher merge rates. This supports treating shared-array batch edits and module-isolated landmark edits as separate regimes.\n")
    report.append("- Higher deletion thresholds correlate with lower merge rates, especially for local git two-dot deletions. This is consistent with H2, but it does not confirm H2 by itself because deletions can also reflect legitimate repair work and because merge outcome is not identical to semantic safety.\n")
    report.append("- Local git stale-distance features add a useful reconstruction layer: non-descendant heads and very large two-dot deletion counts are good audit-prioritization signals, but still require manual inspection.\n")

    OUT_REPORT.write_text("\n".join(report))
    print(f"Wrote extended analysis to {OUT_REPORT}")


if __name__ == "__main__":
    main()
