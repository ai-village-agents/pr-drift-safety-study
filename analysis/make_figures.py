#!/usr/bin/env python3
"""Create small descriptive figures for the PR drift study.

These plots visualize published feature tables only. They are descriptive
summaries of weak labels and merge outcomes, not causal safety estimates.
"""
from pathlib import Path

import numpy as np
import pandas as pd

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

ROOT = Path(__file__).resolve().parents[1]
RESULTS = ROOT / "results"
FIGDIR = RESULTS / "figures"
FEATURES = RESULTS / "pr_level_features.csv"
GIT = RESULTS / "git_pr_metrics.csv"


def save(fig, name: str) -> None:
    FIGDIR.mkdir(parents=True, exist_ok=True)
    path = FIGDIR / name
    fig.tight_layout()
    fig.savefig(path, dpi=180, bbox_inches="tight")
    plt.close(fig)
    print(f"wrote {path.relative_to(ROOT)}")


def load() -> pd.DataFrame:
    df = pd.read_csv(FEATURES)
    if GIT.exists():
        git = pd.read_csv(GIT)
        keep = [c for c in ["number", "git_base_is_ancestor_of_head", "git_commits_behind_base"] if c in git.columns]
        if len(keep) > 1:
            df = df.merge(git[keep], on="number", how="left", suffixes=("", "_gitfile"))
    if "git_base_is_ancestor_of_head" in df.columns:
        df["git_head_not_descendant_of_base"] = (df["git_base_is_ancestor_of_head"] == 0).astype(int)
    return df


def daily_outcomes(df: pd.DataFrame) -> None:
    if not {"created_at", "merged", "risk_comment_label"}.issubset(df.columns):
        print("skip daily_outcomes.png: missing created_at/merged/risk_comment_label")
        return
    d = df.copy()
    d["created_date"] = pd.to_datetime(d["created_at"], utc=True).dt.date
    g = d.groupby("created_date").agg(
        prs=("number", "size"),
        merge_rate=("merged", "mean"),
        risk_comment_rate=("risk_comment_label", "mean"),
    ).reset_index()
    x = np.arange(len(g))
    fig, ax1 = plt.subplots(figsize=(8.5, 4.8))
    ax1.bar(x, g["prs"], color="#d8d8d8", edgecolor="#888888", label="PR count")
    ax1.set_ylabel("PR count")
    ax1.set_xticks(x)
    ax1.set_xticklabels([str(v) for v in g["created_date"]], rotation=30, ha="right")
    ax2 = ax1.twinx()
    ax2.plot(x, g["merge_rate"], marker="o", color="#2c7fb8", label="merge rate")
    ax2.plot(x, g["risk_comment_rate"], marker="o", color="#d95f0e", label="weak risk-label rate")
    ax2.set_ylim(0, 1)
    ax2.set_ylabel("Rate")
    lines, labels = ax1.get_legend_handles_labels()
    lines2, labels2 = ax2.get_legend_handles_labels()
    ax2.legend(lines + lines2, labels + labels2, loc="upper left", frameon=False)
    ax1.set_title("PR volume, merge rate, and weak risk-label rate by day")
    save(fig, "daily_outcomes.png")


def feature_rates(df: pd.DataFrame) -> None:
    features = [
        ("touch_main_js", "touch main.js"),
        ("touch_landmark", "touch landmark"),
        ("touch_anchorage", "touch Anchorage"),
        ("title_cosmic_batch", "cosmic batch title"),
        ("git_head_not_descendant_of_base", "head not descendant"),
    ]
    rows = []
    for col, label in features:
        if col not in df.columns:
            print(f"skip feature {col}: missing column")
            continue
        sub = df[df[col].fillna(0).astype(int) == 1]
        if sub.empty:
            continue
        rows.append((label, len(sub), sub["merged"].mean(), sub["risk_comment_label"].mean()))
    if not rows:
        print("skip feature_merge_risk_rates.png: no feature columns available")
        return
    labels = [f"{r[0]}\n(n={r[1]})" for r in rows]
    merge = [r[2] for r in rows]
    risk = [r[3] for r in rows]
    x = np.arange(len(rows))
    width = 0.36
    fig, ax = plt.subplots(figsize=(9.5, 5.0))
    ax.bar(x - width/2, merge, width, label="merge rate", color="#2c7fb8")
    ax.bar(x + width/2, risk, width, label="weak risk-label rate", color="#d95f0e")
    ax.set_ylim(0, 1)
    ax.set_ylabel("Rate among PRs with feature")
    ax.set_xticks(x)
    ax.set_xticklabels(labels, rotation=20, ha="right")
    ax.legend(frameon=False)
    ax.set_title("Merge and weak risk-label rates for selected PR features")
    save(fig, "feature_merge_risk_rates.png")


def stale_distance(df: pd.DataFrame) -> None:
    if "git_commits_behind_base" not in df.columns:
        print("skip stale_distance_merge_rate.png: missing git_commits_behind_base")
        return
    bins = [-0.1, 0, 1, 5, 50, np.inf]
    labels = ["0", "1", "2-5", "6-50", ">50"]
    d = df.dropna(subset=["git_commits_behind_base"]).copy()
    d["behind_bin"] = pd.cut(d["git_commits_behind_base"], bins=bins, labels=labels)
    g = d.groupby("behind_bin", observed=False).agg(n=("number", "size"), merge_rate=("merged", "mean")).reindex(labels)
    x = np.arange(len(g))
    fig, ax = plt.subplots(figsize=(7.5, 4.8))
    bars = ax.bar(x, g["merge_rate"], color="#756bb1")
    ax.set_ylim(0, 1)
    ax.set_ylabel("Merge rate")
    ax.set_xlabel("Commits behind recorded base")
    ax.set_xticks(x)
    ax.set_xticklabels(labels)
    for bar, n in zip(bars, g["n"]):
        ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.02, f"n={int(n)}", ha="center", va="bottom", fontsize=9)
    ax.set_title("Merge rate by stale-distance bin")
    save(fig, "stale_distance_merge_rate.png")


def main() -> None:
    df = load()
    daily_outcomes(df)
    feature_rates(df)
    stale_distance(df)


if __name__ == "__main__":
    main()
