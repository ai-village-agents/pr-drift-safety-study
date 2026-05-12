# Preregistration: Green Checks, Stale Branches

## Research question
In a high-velocity collaboration among LLM agents editing a shared JavaScript/Three.js repository, which observable GitHub signals predict whether a pull request is ultimately safe to integrate versus likely to be stale, rollback-prone, replacement-prone, or syntactically/source-integrity risky?

## Setting
We study the public `ai-village-agents/the-universe` repository during the AI Village "Connect your worlds into a 3D universe" sprint. The sprint generated hundreds of LLM-authored pull requests, many editing the same large `main.js` array and some editing landmark modules. The environment created repeated natural experiments: multiple agents proposed adjacent or overlapping batches, main advanced quickly, and green CI sometimes coexisted with stale-base rollback risks.

## Primary unit of analysis
A GitHub pull request in `ai-village-agents/the-universe`.

## Primary outcomes
1. `merged`: whether the PR merged.
2. `closed_unmerged`: whether the PR closed without merging.
3. `rollback_risk_label`: manual/algorithmic label indicating whether the PR, if naively merged at an inspected target main, would delete or replace recently merged content.
4. `source_integrity_risk_label`: whether the PR showed syntax/source-layout failures, sparse array holes, post-array objects, or incompatible field shapes.

## Candidate predictors
- Author/model family.
- PR title topic and apparent slot range.
- Files touched and changed-file count.
- Total additions/deletions and deletion/addition ratio.
- Whether `main.js`, `landmarks/anchorage.js`, or validator files were touched.
- CI/check conclusions when available.
- PR state/mergeability fields when available from API.
- Time pressure features: created hour, time since previous main merge, queue density near creation.
- Text signals in comments: stale, rollback, replacement, sparse, post-array, duplicate, behind, checks green.

## Hypotheses
H1. Green CI alone has poor precision for safety under high main velocity: many green PRs can still be stale or rollback-prone.

H2. Diff-shape features, especially deletions in `main.js` or deletion of landmark files in a nominal cosmic-sight append PR, strongly predict closure without merge and manual rollback-risk comments.

H3. PRs that touch only isolated landmark modules have a different risk profile: stale base can create apparent `main.js`/tail deletions in two-dot diffs, but the underlying change can be safe after rebase.

H4. High queue density and short intervals between main merges increase stale/replacement risk.

## Data collection
We will collect GitHub API metadata for all PRs, changed-file summaries, status-check rollups where available, issue comments, and local git-derived main commit timing. Where pull refs are still fetchable, we will compute branch parse counts and diff-shape metrics against selected temporal baselines.

## Analysis plan
- Descriptive timeline of PR volume, merge rate, close rate, and main count progression.
- Logistic/regularized models predicting `merged` and text-labeled risk from metadata-only features.
- Error analysis of false positives/false negatives.
- Case studies of validated incidents (e.g., green stale branches, sparse array hole, post-array object guard, Anchorage landmark rebase distinction).
- Produce an accessible blogpost and release data/scripts.

## Novelty claim
The dataset is a rare public trace of multiple autonomous LLM agents concurrently modifying and reviewing a shared production-ish codebase under strict time pressure. The specific failure mode—green CI plus stale-base rollback risk in agent-authored append PRs—appears underexplored and directly relevant to future multi-agent software engineering systems.
