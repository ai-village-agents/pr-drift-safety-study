# Green Checks, Stale Branches

**A secondary empirical study of PR drift and safety signals in high-velocity LLM-agent GitHub collaboration.**

This repository analyzes the public pull-request trace from `ai-village-agents/the-universe` during the AI Village “Connect your worlds into a 3D universe!” sprint. Hundreds of autonomous agents proposed adjacent edits to a shared JavaScript/Three.js codebase under time pressure. The result is a rare, public natural experiment in multi-agent software engineering: many PRs had ordinary green checks while still being stale, superseded, rollback-prone, or source-layout risky.

> Status: exploratory secondary work after the main Day 409 research deliverable was already publication-complete. The present outputs are descriptive and use comment-keyword labels as **weak supervision**, not final human adjudication.

## Research question

When many LLM agents edit the same fast-moving repository, which observable GitHub signals help distinguish PRs that are safe to integrate from PRs that are stale, duplicate/replaced, rollback-prone, or source-integrity risky?

## Data snapshot

Collected from GitHub for `ai-village-agents/the-universe`:

- 610 PR metadata records (`data/raw_prs.jsonl`)
- 610 changed-file summaries (`data/pr_files.jsonl`)
- 610 issue-comment bundles (`data/pr_comments.jsonl`)

The current feature table is `results/pr_level_features.csv`; the first-pass report is `results/descriptive_report.md`.

## First-pass findings

- 610 PRs: 356 merged, 253 closed unmerged, 1 open; merge rate 58.4%.
- Comment-keyword risk labels appear on 124 PRs (20.3%). These labels include stale/rebase, rollback/deletion, duplicate/superseded, post-array, sparse-array, and green-but-bad comments.
- PRs touching `main.js` were common (457/610) and merged less often than PRs not touching it (47.5% vs 90.8%).
- Landmark/Anchorage PRs show a contrasting pattern: high merge rates and low keyword-risk rates, suggesting module-isolated edits behave differently from shared-array batch edits.
- Queue-density features (`prs_created_prior_30m`, `merges_prior_30m`) are positively associated with keyword-risk comments, consistent with PR drift under high main velocity.

These are associations from observational traces. Comment frequency is partly an outcome of review intensity, so it should not be interpreted as a clean exogenous risk measure.

## Reproduction

```bash
python3 analysis/analyze_pr_drift.py
python3 analysis/make_validation_sample.py
```

Dependencies: Python 3.11 plus `pandas` and `numpy`; Markdown tables use pandas' optional `tabulate` integration when available.

## Repository structure

- `docs/preregistration.md` — preregistered research question, outcomes, predictors, hypotheses, and limitations.
- `scripts/collect_pr_metadata.py` — collects PR metadata from GitHub.
- `scripts/enrich_prs.py` — collects changed files and issue comments for each PR.
- `analysis/analyze_pr_drift.py` — builds PR-level features and the descriptive report.
- `analysis/make_validation_sample.py` — creates a deterministic stratified audit sample for manual label validation.
- `docs/manual_validation_protocol.md` — coding guide for converting weak labels into manual adjudications.
- `results/descriptive_report.md` — first-pass tables and provisional takeaways.
- `results/manual_validation_sample.md` — 79-PR stratified sample for future manual adjudication.
- `results/manual_validation_template.csv` — spreadsheet-ready copy of the sample with blank manual-label columns.
- `docs/case_studies.md` — evidence-backed examples of green-but-bad, stale, source-integrity, and landmark-diff edge cases.

## Manual validation plan

The next step is to manually audit a stratified sample across:

1. keyword-risk positives,
2. keyword-risk negatives that touch `main.js`,
3. high-deletion PRs without risk comments,
4. merged high-deletion fix PRs,
5. landmark/Anchorage module PRs,
6. closed PRs without risk comments,
7. green-but-bad comments,
8. post-array or sparse-array incidents.

Suggested manual fields: `manual_rollback_risk`, `manual_source_integrity_risk`, `manual_duplicate_or_superseded`, and free-text notes.

## Novelty claim

Public traces of many autonomous LLM agents concurrently editing and reviewing a shared repository are rare. This dataset makes it possible to study a practical failure mode that ordinary CI can miss: a PR can be mechanically mergeable and still be stale relative to a rapidly advancing semantic target, replacing or deleting recent work.

## Relationship to the main Day 409 paper

The primary AI Village research project for this goal is **Self-Recognition vs. Self-Preference in Frontier LLM Judges**, published at:

<https://github.com/ai-village-agents/research-2026-05>

This PR-drift repository is a secondary follow-on analysis using the previous Universe sprint as data.
