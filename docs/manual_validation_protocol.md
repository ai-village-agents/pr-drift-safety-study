# Manual validation protocol

This protocol turns the weak comment-keyword labels in `results/pr_level_features.csv` into auditable manual labels for a stratified sample. The template spreadsheet is `results/manual_validation_template.csv`.

## Unit

One pull request from `ai-village-agents/the-universe`. Review the PR page, collected comments, changed-file summary, and (when needed) the diff against the relevant main commit.

## Manual fields

Use values `0`, `1`, or `unclear` unless otherwise noted.

- `manual_rollback_risk`: Would naïvely merging the branch at the reviewed point delete/replace already-merged substantive content or safety guards?
- `manual_source_integrity_risk`: Did the branch contain syntax/source-layout/schema failures such as post-array objects, sparse array holes, invalid position fields, or broken validators?
- `manual_duplicate_or_superseded`: Was the PR closed because another PR already filled the same slot/theme or because it was explicitly superseded?
- `manual_label_confidence`: Suggested scale `low`, `medium`, `high`.
- `manual_notes`: Short evidence note, ideally naming the decisive comment, diff observation, or validation output.

## Adjudication guidance

1. Do not equate `closed_unmerged` with risk. A PR may be closed for timing, duplication, author choice, or because a cleaner replacement landed.
2. Do not equate high deletions with risk. Some repair PRs intentionally delete corrupt code.
3. Treat landmark/Anchorage PRs separately from `main.js` array-batch PRs. A stale two-dot diff may show `main.js` tail deletion even when the intended module change can be safely rebased.
4. A PR can have multiple risks: e.g. source-layout failure first, then same-slot replacement risk after main advances.
5. If only a keyword label exists but there is no inspectable evidence, mark `unclear` rather than forcing a positive.

## Suggested reporting

After adjudication, report precision/recall of the weak keyword labels separately for rollback risk, source-integrity risk, and duplicate/superseded risk. Also report disagreement cases as qualitative examples; they are likely more informative than the aggregate score alone.
