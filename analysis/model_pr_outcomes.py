#!/usr/bin/env python3
"""Multivariable descriptive models for PR drift outcomes.

This appendix complements marginal tables with simple logistic regressions fitted in
pure NumPy. The models are descriptive: coefficients are adjusted associations in
this sprint trace, not causal estimates and not substitutes for manual safety
labels.
"""
from __future__ import annotations

import math
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
RESULTS = ROOT / "results"
OUT = RESULTS / "model_outcomes.md"


def logistic_fit(X: np.ndarray, y: np.ndarray, max_iter: int = 100, ridge: float = 1e-6):
    beta = np.zeros(X.shape[1])
    for _ in range(max_iter):
        eta = np.clip(X @ beta, -35, 35)
        p = 1 / (1 + np.exp(-eta))
        w = np.clip(p * (1 - p), 1e-8, None)
        z = eta + (y - p) / w
        WX = X * w[:, None]
        h = X.T @ WX + ridge * np.eye(X.shape[1])
        rhs = X.T @ (w * z)
        try:
            new_beta = np.linalg.solve(h, rhs)
        except np.linalg.LinAlgError:
            new_beta = np.linalg.pinv(h) @ rhs
        if np.max(np.abs(new_beta - beta)) < 1e-8:
            beta = new_beta
            break
        beta = new_beta
    eta = np.clip(X @ beta, -35, 35)
    p = 1 / (1 + np.exp(-eta))
    w = np.clip(p * (1 - p), 1e-8, None)
    h = X.T @ (X * w[:, None]) + ridge * np.eye(X.shape[1])
    try:
        cov = np.linalg.inv(h)
    except np.linalg.LinAlgError:
        cov = np.linalg.pinv(h)
    se = np.sqrt(np.maximum(np.diag(cov), 0))
    return beta, se, p


def auc_score(y: np.ndarray, p: np.ndarray) -> float:
    order = np.argsort(p)
    ranks = np.empty_like(order, dtype=float)
    ranks[order] = np.arange(1, len(p) + 1)
    pos = y == 1
    n_pos = int(pos.sum())
    n_neg = int((~pos).sum())
    if n_pos == 0 or n_neg == 0:
        return float("nan")
    return float((ranks[pos].sum() - n_pos * (n_pos + 1) / 2) / (n_pos * n_neg))


def make_design(df: pd.DataFrame, specs: list[tuple[str, str]]):
    cols = [np.ones(len(df))]
    names = ["intercept"]
    scales = {"intercept": (0.0, 1.0)}
    for name, kind in specs:
        if name not in df.columns:
            continue
        x = df[name].astype(float).fillna(0).to_numpy()
        if kind == "binary":
            cols.append(x)
            names.append(name)
            scales[name] = (0.0, 1.0)
        elif kind == "log1p":
            z = np.log1p(np.maximum(x, 0))
            mean = float(np.mean(z))
            sd = float(np.std(z)) or 1.0
            cols.append((z - mean) / sd)
            names.append(f"log1p({name}) z")
            scales[f"log1p({name}) z"] = (mean, sd)
        elif kind == "z":
            mean = float(np.mean(x))
            sd = float(np.std(x)) or 1.0
            cols.append((x - mean) / sd)
            names.append(f"{name} z")
            scales[f"{name} z"] = (mean, sd)
    return np.column_stack(cols), names, scales


def model_table(df: pd.DataFrame, outcome: str, specs: list[tuple[str, str]], label: str):
    y = df[outcome].astype(int).to_numpy()
    X, names, _ = make_design(df, specs)
    beta, se, pred = logistic_fit(X, y)
    rows = []
    for n, b, s in zip(names, beta, se):
        z = b / s if s > 0 else float("nan")
        # Normal approximation, enough for descriptive screening.
        pval = math.erfc(abs(z) / math.sqrt(2)) if math.isfinite(z) else float("nan")
        rows.append({
            "term": n,
            "log_odds": b,
            "SE": s,
            "odds_ratio": math.exp(max(min(b, 20), -20)),
            "z": z,
            "p_approx": pval,
        })
    table = pd.DataFrame(rows)
    auc = auc_score(y, pred)
    mean_pred_pos = float(pred[y == 1].mean()) if (y == 1).any() else float("nan")
    mean_pred_neg = float(pred[y == 0].mean()) if (y == 0).any() else float("nan")
    summary = {
        "model": label,
        "outcome": outcome,
        "N": len(df),
        "positive_rate": float(y.mean()),
        "AUC_in_sample": auc,
        "mean_pred_positive_cases": mean_pred_pos,
        "mean_pred_negative_cases": mean_pred_neg,
    }
    return summary, table


def md_table(df: pd.DataFrame) -> str:
    d = df.copy()
    for c in d.columns:
        if pd.api.types.is_float_dtype(d[c]):
            d[c] = d[c].map(lambda x: "" if pd.isna(x) else f"{x:.3f}")
    return d.to_markdown(index=False)


def main():
    df = pd.read_csv(RESULTS / "pr_level_features.csv")
    df = df[df["open"] == 0].copy()
    df["git_head_not_descendant_of_base"] = 1 - df.get("git_base_is_ancestor_of_head", pd.Series(1, index=df.index)).fillna(1).astype(int)
    df["git_deletions_gt10"] = (df.get("git_deletions", df["deletions"]) > 10).astype(int)
    df["api_deletions_gt10"] = (df["deletions"] > 10).astype(int)

    base_specs = [
        ("touch_main_js", "binary"),
        ("touch_landmark", "binary"),
        ("title_cosmic_batch", "binary"),
        ("title_fix", "binary"),
        ("api_deletions_gt10", "binary"),
        ("prs_created_prior_30m", "z"),
        ("merges_prior_30m", "z"),
    ]
    git_specs = [
        ("touch_main_js", "binary"),
        ("touch_landmark", "binary"),
        ("title_cosmic_batch", "binary"),
        ("title_fix", "binary"),
        ("git_head_not_descendant_of_base", "binary"),
        ("git_deletions_gt10", "binary"),
        ("git_commits_behind_base", "log1p"),
        ("prs_created_prior_30m", "z"),
        ("merges_prior_30m", "z"),
    ]
    risk_specs = [
        ("touch_main_js", "binary"),
        ("touch_landmark", "binary"),
        ("title_cosmic_batch", "binary"),
        ("git_head_not_descendant_of_base", "binary"),
        ("git_deletions_gt10", "binary"),
        ("prs_created_prior_30m", "z"),
        ("merges_prior_30m", "z"),
    ]

    models = [
        model_table(df, "merged", base_specs, "Merge outcome: API/topic/time features"),
        model_table(df, "merged", git_specs, "Merge outcome: adding local git stale metrics"),
        model_table(df, "risk_comment_label", risk_specs, "Keyword-risk outcome: git/topic/time features"),
    ]

    report = ["# Multivariable PR outcome models\n", "These pure-NumPy logistic regressions are descriptive adjusted associations over the Universe sprint PR trace. They are not causal estimates, not cross-validated production classifiers, and not substitutes for manual safety adjudication. Coefficients are log-odds; odds ratios above 1 indicate higher odds of the modeled outcome.\n"]
    for summary, table in models:
        report.append(f"## {summary['model']}\n")
        report.append(md_table(pd.DataFrame([summary])))
        report.append("\n")
        report.append(md_table(table))
        report.append("\n")
    report.append("## Reading notes\n")
    report.append("- The git-augmented merge model should be read mainly as a sanity check that stale reconstruction signals add information beyond topic/file-touch labels.\n")
    report.append("- Very large negative merge coefficients for non-descendant/stale terms reflect the review process in this trace: reviewers often closed stale branches rather than rebasing them. That does not prove every stale branch was semantically unsafe.\n")
    report.append("- The keyword-risk model predicts comment labels, so it partly models reviewer attention and language rather than latent safety. Manual validation remains necessary.\n")
    OUT.write_text("\n".join(report))
    print(f"Wrote {OUT}")


if __name__ == "__main__":
    main()
