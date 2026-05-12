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

## Git-derived base/head diff metrics

These metrics are computed locally with `git diff base_sha..head_sha` after fetching all PR heads. They are independent of GitHub API file summaries and capture stale-branch two-dot diffs that can delete already-current content. They are still syntactic triage signals, not semantic safety labels.

|   PRs_with_git_metrics |   base_commits_available |   head_commits_available |   merge_shas_available |   head_not_descendant_of_base |   mean_git_deletions |   median_git_deletions |   max_git_deletions |
|-----------------------:|-------------------------:|-------------------------:|-----------------------:|------------------------------:|---------------------:|-----------------------:|--------------------:|
|                    610 |                      610 |                      610 |                    356 |                           144 |              275.034 |                      0 |               48969 |

### Git metric distributions

| metric                  |    mean |   median |   p90 |   max |
|:------------------------|--------:|---------:|------:|------:|
| git_commits_ahead_base  |   1.039 |      1   |   1   |     5 |
| git_commits_behind_base |   3.749 |      0   |   1   |   823 |
| git_files_changed       |   1.721 |      1   |   2   |   128 |
| git_additions           | 119.328 |     32.5 | 214.1 |  2221 |
| git_deletions           | 275.034 |      0   | 202   | 48969 |

### API vs local-git agreement checks

| comparison                          |   mismatches |
|:------------------------------------|-------------:|
| main.js touch API vs git            |            4 |
| landmark touch API vs git           |           73 |
| API deletion count differs from git |          142 |

### Largest git two-dot deletion PRs

|   number | title                                                                                         | user                 |   merged |   closed_unmerged |   git_commits_behind_base |   git_commits_ahead_base |   git_files_changed |   git_additions |   git_deletions |   git_touch_main_js |   git_touch_landmark |   risk_comment_label |
|---------:|:----------------------------------------------------------------------------------------------|:---------------------|---------:|------------------:|--------------------------:|-------------------------:|--------------------:|----------------:|----------------:|--------------------:|---------------------:|---------------------:|
|      310 | feat(landmark): Add Hostile Environment World Landmark                                        | gemini-25-pro-collab |        0 |                 1 |                       823 |                        2 |                 107 |            1100 |           48969 |                   1 |                    1 |                    1 |
|      299 | Add Hostile Environment World landmark                                                        | gemini-25-pro-collab |        0 |                 1 |                       816 |                        1 |                 106 |            1064 |           47982 |                   1 |                    1 |                    0 |
|        2 | [EMERGENCY] Reconcile universe configuration - restore all 14+ worlds                         | deepseek-v32         |        0 |                 1 |                       394 |                        2 |                 128 |             271 |           33687 |                   1 |                    1 |                    1 |
|      524 | feat: add 25 exotic matter sights (13126-13150)                                               | gemini-25-pro-collab |        0 |                 1 |                        24 |                        1 |                   3 |              50 |            3431 |                   1 |                    1 |                    0 |
|      284 | Batch 104: High-Energy Physics (11176-11200)                                                  | claudehaiku45        |        0 |                 1 |                         5 |                        1 |                   3 |             107 |            1952 |                   1 |                    1 |                    1 |
|      222 | Batch: Exotic Particle Physics & Condensed Matter Anomalies (10,826-10,850)                   | gemini-3-1-pro       |        1 |                 0 |                         0 |                        1 |                   1 |             176 |            1508 |                   1 |                    0 |                    0 |
|      482 | feat: add 25 exotic matter sights (13001-13025)                                               | gemini-25-pro-collab |        0 |                 1 |                         6 |                        1 |                   2 |             326 |             838 |                   1 |                    1 |                    1 |
|      611 | Batch 205: Neutron Star Equation of State (13751-13775)                                       | claudehaiku45        |        0 |                 1 |                         0 |                        1 |                   1 |              26 |             773 |                   1 |                    0 |                    0 |
|      560 | Batch: Computational Astrophysics – Numerical Methods & HPC (25 cosmic sights, 13,351-13,375) | deepseek-v32         |        0 |                 1 |                         5 |                        1 |                   2 |             151 |             744 |                   1 |                    1 |                    1 |
|      275 | Fix hub regression: restore missing bootstrap initialization                                  | claudehaiku45        |        0 |                 1 |                         4 |                        1 |                   2 |            1456 |             739 |                   1 |                    1 |                    1 |
|      329 | Batch 127: Computational Astrophysics & Numerical Methods (11,576-11,600)                     | deepseek-v32         |        0 |                 1 |                         6 |                        2 |                   3 |              81 |             689 |                   1 |                    1 |                    1 |
|      142 | Add batch 62: Stellar Atmospheres & Wind Phenomena (23 sights, 10,101-10,123)                 | claudehaiku45        |        0 |                 1 |                         6 |                        1 |                   2 |             151 |             664 |                   1 |                    1 |                    1 |

### Largest deletion PRs where head is not a descendant of base

|   number | title                                                                                         | user                 |   merged |   closed_unmerged |   git_commits_behind_base |   git_files_changed |   git_additions |   git_deletions |   risk_comment_label |
|---------:|:----------------------------------------------------------------------------------------------|:---------------------|---------:|------------------:|--------------------------:|--------------------:|----------------:|----------------:|---------------------:|
|      310 | feat(landmark): Add Hostile Environment World Landmark                                        | gemini-25-pro-collab |        0 |                 1 |                       823 |                 107 |            1100 |           48969 |                    1 |
|      299 | Add Hostile Environment World landmark                                                        | gemini-25-pro-collab |        0 |                 1 |                       816 |                 106 |            1064 |           47982 |                    0 |
|        2 | [EMERGENCY] Reconcile universe configuration - restore all 14+ worlds                         | deepseek-v32         |        0 |                 1 |                       394 |                 128 |             271 |           33687 |                    1 |
|      524 | feat: add 25 exotic matter sights (13126-13150)                                               | gemini-25-pro-collab |        0 |                 1 |                        24 |                   3 |              50 |            3431 |                    0 |
|      284 | Batch 104: High-Energy Physics (11176-11200)                                                  | claudehaiku45        |        0 |                 1 |                         5 |                   3 |             107 |            1952 |                    1 |
|      482 | feat: add 25 exotic matter sights (13001-13025)                                               | gemini-25-pro-collab |        0 |                 1 |                         6 |                   2 |             326 |             838 |                    1 |
|      560 | Batch: Computational Astrophysics – Numerical Methods & HPC (25 cosmic sights, 13,351-13,375) | deepseek-v32         |        0 |                 1 |                         5 |                   2 |             151 |             744 |                    1 |
|      275 | Fix hub regression: restore missing bootstrap initialization                                  | claudehaiku45        |        0 |                 1 |                         4 |                   2 |            1456 |             739 |                    1 |
|      329 | Batch 127: Computational Astrophysics & Numerical Methods (11,576-11,600)                     | deepseek-v32         |        0 |                 1 |                         6 |                   3 |              81 |             689 |                    1 |
|      142 | Add batch 62: Stellar Atmospheres & Wind Phenomena (23 sights, 10,101-10,123)                 | claudehaiku45        |        0 |                 1 |                         6 |                   2 |             151 |             664 |                    1 |
|      140 | Add batch 61: Cosmological Structures & Large-Scale Phenomena (25 sights, 10,180-10,204)      | claudehaiku45        |        0 |                 1 |                         5 |                   2 |             153 |             639 |                    1 |
|      138 | Restore getDirectoryEntries DOM query                                                         | gpt-5-5-village      |        0 |                 1 |                         4 |                   2 |               0 |             578 |                    0 |

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

| feature                      | kind    |   n_feature |   target_rate_if_feature |   target_rate_if_absent |   difference |   corr |
|:-----------------------------|:--------|------------:|-------------------------:|------------------------:|-------------:|-------:|
| comment_count                | numeric |         610 |                          |                         |              | -0.676 |
| git_base_is_ancestor_of_head | binary  |         466 |                    0.76  |                   0.014 |        0.746 |  0.642 |
| git_merge_base_is_base       | binary  |         466 |                    0.76  |                   0.014 |        0.746 |  0.642 |
| git_deletion_ratio           | numeric |         610 |                          |                         |              | -0.52  |
| comment_chars                | numeric |         610 |                          |                         |              | -0.487 |
| kw_stale                     | binary  |          76 |                    0.053 |                   0.659 |       -0.607 | -0.406 |
| touch_anchorage              | binary  |         129 |                    0.961 |                   0.482 |        0.479 |  0.397 |
| title_landmark               | binary  |         136 |                    0.949 |                   0.479 |        0.47  |  0.397 |
| git_touch_main_js            | binary  |         459 |                    0.473 |                   0.921 |       -0.448 | -0.392 |
| touch_landmark               | binary  |         135 |                    0.941 |                   0.482 |        0.459 |  0.386 |
| touch_main_js                | binary  |         457 |                    0.475 |                   0.908 |       -0.434 | -0.381 |
| title_cosmic_batch           | binary  |         442 |                    0.477 |                   0.863 |       -0.386 | -0.35  |
| kw_duplicate                 | binary  |          52 |                    0.019 |                   0.636 |       -0.617 | -0.349 |
| kw_rollback                  | binary  |          29 |                    0.034 |                   0.611 |       -0.577 | -0.249 |
| kw_merge_safe_positive       | binary  |          26 |                    0.077 |                   0.606 |       -0.529 | -0.217 |

## Feature screen: association with keyword risk comments

| feature                      | kind    |   n_feature |   target_rate_if_feature |   target_rate_if_absent |   difference |   corr |
|:-----------------------------|:--------|------------:|-------------------------:|------------------------:|-------------:|-------:|
| comment_count                | numeric |         610 |                          |                         |              |  0.785 |
| kw_stale                     | binary  |          76 |                    1     |                   0.09  |        0.91  |  0.747 |
| comment_chars                | numeric |         610 |                          |                         |              |  0.708 |
| kw_duplicate                 | binary  |          52 |                    1     |                   0.129 |        0.871 |  0.604 |
| kw_rollback                  | binary  |          29 |                    1     |                   0.164 |        0.836 |  0.442 |
| git_merge_base_is_base       | binary  |         466 |                    0.107 |                   0.514 |       -0.407 | -0.429 |
| git_base_is_ancestor_of_head | binary  |         466 |                    0.107 |                   0.514 |       -0.407 | -0.429 |
| git_deletion_ratio           | numeric |         610 |                          |                         |              |  0.406 |
| kw_merge_safe_positive       | binary  |          26 |                    0.962 |                   0.17  |        0.792 |  0.398 |
| prs_created_prior_30m        | numeric |         610 |                          |                         |              |  0.306 |
| merges_prior_30m             | numeric |         610 |                          |                         |              |  0.272 |
| git_touch_main_js            | binary  |         459 |                    0.257 |                   0.04  |        0.217 |  0.233 |
| touch_anchorage              | binary  |         129 |                    0.023 |                   0.252 |       -0.228 | -0.232 |
| kw_not_merge_safe            | binary  |           8 |                    1     |                   0.193 |        0.807 |  0.228 |
| touch_main_js                | binary  |         457 |                    0.256 |                   0.046 |        0.21  |  0.226 |

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

- Local git metrics sharpen the stale-branch picture: every PR base/head commit was recoverable, but 144 PR heads were not descendants of their recorded base and some two-dot diffs implied tens of thousands of deletions. These are triage flags, not automatic failure labels.
