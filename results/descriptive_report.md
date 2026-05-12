# PR Drift Safety Study: descriptive analysis

This is a first-pass descriptive analysis of GitHub PR metadata, changed-file summaries, and issue comments from `ai-village-agents/the-universe`. Risk labels are keyword-derived from PR comments, not final manual adjudications.

## Coverage

|   PRs |   merged |   closed_unmerged |   open |   merge_rate |   risk_comment_labels |   risk_comment_rate |   touch_main_js_rate |
|------:|---------:|------------------:|-------:|-------------:|----------------------:|--------------------:|---------------------:|
|   610 |      356 |               253 |      1 |        0.584 |                   124 |               0.203 |                0.749 |

## PR volume by creation date

| created_date   |   prs |   merged |   closed_unmerged |   open |   merge_rate |   risk_comment_rate |   mean_deletions |
|:---------------|------:|---------:|------------------:|-------:|-------------:|--------------------:|-----------------:|
| 2026-05-04     |     2 |        1 |                 1 |      0 |        0.5   |               0.5   |            2     |
| 2026-05-06     |    91 |       66 |                25 |      0 |        0.725 |               0.022 |            2.604 |
| 2026-05-07     |   184 |      121 |                63 |      0 |        0.658 |               0.092 |           15.951 |
| 2026-05-08     |   333 |      168 |               164 |      1 |        0.505 |               0.312 |            4.039 |

## File/topic touch signals

| signal             |   prs |   merge_rate |   risk_comment_rate |
|:-------------------|------:|-------------:|--------------------:|
| touch_main_js      |   457 |        0.475 |               0.256 |
| touch_landmark     |   135 |        0.941 |               0.037 |
| touch_anchorage    |   129 |        0.961 |               0.023 |
| touch_validator    |     3 |        0.667 |               0.333 |
| title_cosmic_batch |   442 |        0.477 |               0.244 |
| title_landmark     |   136 |        0.949 |               0.044 |
| title_fix          |    38 |        0.632 |               0.211 |

## Comment keyword labels

| keyword_label       |   prs |   merge_rate |
|:--------------------|------:|-------------:|
| stale               |    76 |        0.053 |
| duplicate           |    52 |        0.019 |
| rollback            |    29 |        0.034 |
| merge_safe_positive |    26 |        0.077 |
| not_merge_safe      |     8 |        0     |
| post_array          |     7 |        0     |
| green_but_bad       |     2 |        0.5   |
| sparse              |     1 |        0     |

## Authors with at least 10 PRs

| user                    |   prs |   merged |   closed_unmerged |   open |   merge_rate |   risk_comment_rate |   main_js_rate |   mean_deletions |
|:------------------------|------:|---------:|------------------:|-------:|-------------:|--------------------:|---------------:|-----------------:|
| claude-opus-4-5         |   142 |      101 |                41 |      0 |        0.711 |               0.113 |          1     |            1.507 |
| claude-opus-4-7-village |   125 |      123 |                 2 |      0 |        0.984 |               0.016 |          0.008 |            0.744 |
| gemini-3-1-pro          |   118 |       59 |                58 |      1 |        0.5   |               0.119 |          0.966 |           19.593 |
| claudehaiku45           |   100 |       27 |                73 |      0 |        0.27  |               0.28  |          0.97  |           10.27  |
| kimi-k26                |    54 |       17 |                37 |      0 |        0.315 |               0.63  |          0.944 |            4.593 |
| deepseek-v32            |    20 |        3 |                17 |      0 |        0.15  |               0.65  |          0.75  |            4.55  |
| gpt-5-4                 |    19 |        8 |                11 |      0 |        0.421 |               0.526 |          0.789 |            7.632 |
| gpt-5-5-village         |    18 |       13 |                 5 |      0 |        0.722 |               0.167 |          0.667 |           16.833 |
| gemini-25-pro-collab    |    10 |        2 |                 8 |      0 |        0.2   |               0.4   |          1     |            8.5   |

## Feature screen: association with merge outcome

| feature                | kind    |   n_feature |   target_rate_if_feature |   target_rate_if_absent |   difference |   corr |
|:-----------------------|:--------|------------:|-------------------------:|------------------------:|-------------:|-------:|
| comment_count          | numeric |         610 |                          |                         |              | -0.676 |
| comment_chars          | numeric |         610 |                          |                         |              | -0.487 |
| kw_stale               | binary  |          76 |                    0.053 |                   0.659 |       -0.607 | -0.406 |
| touch_anchorage        | binary  |         129 |                    0.961 |                   0.482 |        0.479 |  0.397 |
| title_landmark         | binary  |         136 |                    0.949 |                   0.479 |        0.47  |  0.397 |
| touch_landmark         | binary  |         135 |                    0.941 |                   0.482 |        0.459 |  0.386 |
| touch_main_js          | binary  |         457 |                    0.475 |                   0.908 |       -0.434 | -0.381 |
| title_cosmic_batch     | binary  |         442 |                    0.477 |                   0.863 |       -0.386 | -0.35  |
| kw_duplicate           | binary  |          52 |                    0.019 |                   0.636 |       -0.617 | -0.349 |
| kw_rollback            | binary  |          29 |                    0.034 |                   0.611 |       -0.577 | -0.249 |
| kw_merge_safe_positive | binary  |          26 |                    0.077 |                   0.606 |       -0.529 | -0.217 |
| prs_created_prior_30m  | numeric |         610 |                          |                         |              | -0.211 |
| merges_prior_30m       | numeric |         610 |                          |                         |              | -0.174 |
| kw_not_merge_safe      | binary  |           8 |                    0     |                   0.591 |       -0.591 | -0.136 |
| kw_post_array          | binary  |           7 |                    0     |                   0.59  |       -0.59  | -0.128 |

## Feature screen: association with keyword risk comments

| feature                | kind    |   n_feature |   target_rate_if_feature |   target_rate_if_absent |   difference |   corr |
|:-----------------------|:--------|------------:|-------------------------:|------------------------:|-------------:|-------:|
| comment_count          | numeric |         610 |                          |                         |              |  0.785 |
| kw_stale               | binary  |          76 |                    1     |                   0.09  |        0.91  |  0.747 |
| comment_chars          | numeric |         610 |                          |                         |              |  0.708 |
| kw_duplicate           | binary  |          52 |                    1     |                   0.129 |        0.871 |  0.604 |
| kw_rollback            | binary  |          29 |                    1     |                   0.164 |        0.836 |  0.442 |
| kw_merge_safe_positive | binary  |          26 |                    0.962 |                   0.17  |        0.792 |  0.398 |
| prs_created_prior_30m  | numeric |         610 |                          |                         |              |  0.306 |
| merges_prior_30m       | numeric |         610 |                          |                         |              |  0.272 |
| touch_anchorage        | binary  |         129 |                    0.023 |                   0.252 |       -0.228 | -0.232 |
| kw_not_merge_safe      | binary  |           8 |                    1     |                   0.193 |        0.807 |  0.228 |
| touch_main_js          | binary  |         457 |                    0.256 |                   0.046 |        0.21  |  0.226 |
| touch_landmark         | binary  |         135 |                    0.037 |                   0.251 |       -0.213 | -0.22  |
| kw_post_array          | binary  |           7 |                    1     |                   0.194 |        0.806 |  0.213 |
| title_landmark         | binary  |         136 |                    0.044 |                   0.249 |       -0.205 | -0.212 |
| title_cosmic_batch     | binary  |         442 |                    0.244 |                   0.095 |        0.149 |  0.166 |

## Highest-deletion PRs

|   number | title                                                                       | user            |   merged |   closed_unmerged |   deletions |   additions |   files_changed |   touch_main_js |   risk_comment_label |
|---------:|:----------------------------------------------------------------------------|:----------------|---------:|------------------:|------------:|------------:|----------------:|----------------:|---------------------:|
|      222 | Batch: Exotic Particle Physics & Condensed Matter Anomalies (10,826-10,850) | gemini-3-1-pro  |        1 |                 0 |        1508 |         176 |               1 |               1 |                    0 |
|      611 | Batch 205: Neutron Star Equation of State (13751-13775)                     | claudehaiku45   |        0 |                 1 |         773 |          26 |               1 |               1 |                    0 |
|      192 | Fix: Move High-Energy Stellar Phenomena (10,576-10,600) to cosmicSights     | gemini-3-1-pro  |        0 |                 1 |         179 |          27 |               1 |               1 |                    0 |
|      193 | Fix: Restore shootingStars array                                            | gemini-3-1-pro  |        1 |                 0 |         178 |           1 |               1 |               1 |                    0 |
|      376 | Fix stray syntax block at end of main.js                                    | gemini-3-1-pro  |        0 |                 1 |         150 |           0 |               1 |               1 |                    1 |
|      381 | Remove dead code blocks after initDiagnosticsPanel                          | gemini-3-1-pro  |        1 |                 0 |         150 |           0 |               1 |               1 |                    0 |
|      138 | Restore getDirectoryEntries DOM query                                       | gpt-5-5-village |        0 |                 1 |         149 |           1 |               1 |               1 |                    0 |
|      275 | Fix hub regression: restore missing bootstrap initialization                | claudehaiku45   |        0 |                 1 |         131 |        1456 |               2 |               1 |                    1 |
|      125 | Restore getDirectoryEntries after accidental sight injection                | gpt-5-4         |        1 |                 0 |         128 |           1 |               1 |               1 |                    1 |
|      134 | 🚨 Hotfix: Restore getDirectoryEntries() function                            | claude-opus-4-5 |        1 |                 0 |         127 |           1 |               1 |               1 |                    0 |
|      128 | Hotfix: Restore getDirectoryEntries() to only return DOM entries            | kimi-k26        |        0 |                 1 |         102 |           1 |               1 |               1 |                    1 |
|      131 | Fix: Restore getDirectoryEntries() to only return DOM entries               | claudehaiku45   |        0 |                 1 |         102 |           1 |               1 |               1 |                    1 |

## Keyword-risk examples

|   number | title                                                                                                                          | user            |   merged |   closed_unmerged |   deletions |   additions |   kw_stale |   kw_rollback |   kw_sparse |   kw_post_array |   kw_duplicate |   kw_green_but_bad |
|---------:|:-------------------------------------------------------------------------------------------------------------------------------|:----------------|---------:|------------------:|------------:|------------:|-----------:|--------------:|------------:|----------------:|---------------:|-------------------:|
|      594 | Batch: Variable Star Classifications (25 cosmic sights, 13601-13625)                                                           | claude-opus-4-5 |        0 |                 1 |           7 |          32 |          1 |             1 |           0 |               0 |              0 |                  0 |
|        2 | [EMERGENCY] Reconcile universe configuration - restore all 14+ worlds                                                          | deepseek-v32    |        0 |                 1 |           4 |         239 |          1 |             1 |           0 |               0 |              0 |                  0 |
|      442 | Batch: Advanced Computational Astrophysics Methods (12476-12500)                                                               | deepseek-v32    |        0 |                 1 |           2 |         201 |          1 |             1 |           0 |               0 |              0 |                  0 |
|      478 | Batch: Advanced Computational Astrophysics Methods (12726-12750)                                                               | deepseek-v32    |        0 |                 1 |           2 |         202 |          1 |             1 |           0 |               0 |              0 |                  0 |
|      511 | Batch: Galactic Magnetic Fields (25 cosmic sights, 13051-13075)                                                                | kimi-k26        |        0 |                 1 |           1 |          26 |          1 |             1 |           0 |               1 |              0 |                  0 |
|      515 | Batch: Advanced Computational Astrophysics Part 3 - Multi-Messenger & Machine Learning Methods (25 cosmic sights, 13251-13275) | deepseek-v32    |        0 |                 1 |           1 |         202 |          1 |             1 |           0 |               0 |              0 |                  0 |
|      526 | Batch: Pulsar Glitch Phenomena (25 cosmic sights, 13126-13150)                                                                 | kimi-k26        |        0 |                 1 |           1 |          26 |          1 |             1 |           0 |               0 |              1 |                  0 |
|      555 | Batch: Quasar Variability Types (25 cosmic sights, 13351-13375)                                                                | claude-opus-4-5 |        0 |                 1 |           1 |          26 |          1 |             1 |           0 |               1 |              0 |                  0 |
|      561 | Batch: Magnetar Physics (25 cosmic sights, 13376-13400)                                                                        | claude-opus-4-5 |        0 |                 1 |           1 |          26 |          1 |             1 |           0 |               0 |              1 |                  0 |
|      572 | Batch: Gravitational Wave Source Populations (25 cosmic sights, 13451-13475)                                                   | kimi-k26        |        0 |                 1 |           1 |          26 |          1 |             1 |           0 |               0 |              0 |                  0 |
|      574 | Batch: Interstellar Medium Phases (25 cosmic sights, 13476-13500)                                                              | claude-opus-4-5 |        0 |                 1 |           1 |          26 |          1 |             1 |           0 |               0 |              0 |                  0 |
|      604 | Batch: Protostellar Environments (25 cosmic sights, 13726-13750)                                                               | kimi-k26        |        0 |                 1 |           1 |          26 |          1 |             1 |           0 |               0 |              1 |                  0 |

## Provisional takeaways

- The dataset is now complete for PR metadata, file summaries, and issue comments.

- Keyword labels are useful for triage but should be treated as weak supervision; the next step is manual validation of a stratified sample, especially high-deletion and stale/rollback-commented PRs.

- Deletion-heavy diffs, `main.js` touches, and queue-density features are available for testing the preregistered stale/rollback-risk hypotheses.
