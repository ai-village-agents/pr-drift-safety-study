# Multivariable PR outcome models

These pure-NumPy logistic regressions are descriptive adjusted associations over the Universe sprint PR trace. They are not causal estimates, not cross-validated production classifiers, and not substitutes for manual safety adjudication. Coefficients are log-odds; odds ratios above 1 indicate higher odds of the modeled outcome.

## Merge outcome: API/topic/time features

| model                                  | outcome   |   N |   positive_rate |   AUC_in_sample |   mean_pred_positive_cases |   mean_pred_negative_cases |
|:---------------------------------------|:----------|----:|----------------:|----------------:|---------------------------:|---------------------------:|
| Merge outcome: API/topic/time features | merged    | 609 |           0.585 |            0.74 |                      0.663 |                      0.474 |


| term                    |   log_odds |    SE |   odds_ratio |      z |   p_approx |
|:------------------------|-----------:|------:|-------------:|-------:|-----------:|
| intercept               |      0.766 | 0.51  |        2.151 |  1.501 |      0.133 |
| touch_main_js           |     -0.707 | 0.555 |        0.493 | -1.274 |      0.203 |
| touch_landmark          |      2.075 | 0.592 |        7.964 |  3.504 |      0     |
| title_cosmic_batch      |     -0.112 | 0.494 |        0.894 | -0.227 |      0.82  |
| title_fix               |     -0.145 | 0.468 |        0.865 | -0.311 |      0.756 |
| api_deletions_gt10      |     -0.635 | 0.538 |        0.53  | -1.182 |      0.237 |
| prs_created_prior_30m z |     -0.539 | 0.2   |        0.583 | -2.695 |      0.007 |
| merges_prior_30m z      |      0.146 | 0.2   |        1.158 |  0.732 |      0.464 |


## Merge outcome: adding local git stale metrics

| model                                         | outcome   |   N |   positive_rate |   AUC_in_sample |   mean_pred_positive_cases |   mean_pred_negative_cases |
|:----------------------------------------------|:----------|----:|----------------:|----------------:|---------------------------:|---------------------------:|
| Merge outcome: adding local git stale metrics | merged    | 609 |           0.585 |           0.888 |                      0.791 |                      0.294 |


| term                             |   log_odds |    SE |   odds_ratio |      z |   p_approx |
|:---------------------------------|-----------:|------:|-------------:|-------:|-----------:|
| intercept                        |      0.95  | 0.679 |        2.586 |  1.399 |      0.162 |
| touch_main_js                    |      0.42  | 0.625 |        1.523 |  0.673 |      0.501 |
| touch_landmark                   |      3.546 | 0.929 |       34.677 |  3.816 |      0     |
| title_cosmic_batch               |     -0.759 | 0.661 |        0.468 | -1.148 |      0.251 |
| title_fix                        |     -0.097 | 0.582 |        0.908 | -0.167 |      0.868 |
| git_head_not_descendant_of_base  |     -4.738 | 1.375 |        0.009 | -3.447 |      0.001 |
| git_deletions_gt10               |     -0.781 | 0.672 |        0.458 | -1.161 |      0.246 |
| log1p(git_commits_behind_base) z |     -0.345 | 0.525 |        0.708 | -0.657 |      0.511 |
| prs_created_prior_30m z          |     -0.471 | 0.251 |        0.624 | -1.875 |      0.061 |
| merges_prior_30m z               |      0.091 | 0.252 |        1.095 |  0.36  |      0.719 |


## Keyword-risk outcome: git/topic/time features

| model                                         | outcome            |   N |   positive_rate |   AUC_in_sample |   mean_pred_positive_cases |   mean_pred_negative_cases |
|:----------------------------------------------|:-------------------|----:|----------------:|----------------:|---------------------------:|---------------------------:|
| Keyword-risk outcome: git/topic/time features | risk_comment_label | 609 |           0.204 |           0.847 |                      0.443 |                      0.142 |


| term                            |   log_odds |    SE |   odds_ratio |      z |   p_approx |
|:--------------------------------|-----------:|------:|-------------:|-------:|-----------:|
| intercept                       |     -1.673 | 0.645 |        0.188 | -2.593 |      0.01  |
| touch_main_js                   |      1.074 | 0.723 |        2.927 |  1.486 |      0.137 |
| touch_landmark                  |     -2.097 | 0.745 |        0.123 | -2.813 |      0.005 |
| title_cosmic_batch              |     -1.605 | 0.569 |        0.201 | -2.82  |      0.005 |
| git_head_not_descendant_of_base |      2.402 | 0.691 |       11.044 |  3.477 |      0.001 |
| git_deletions_gt10              |     -0.492 | 0.693 |        0.611 | -0.71  |      0.478 |
| prs_created_prior_30m z         |      0.778 | 0.267 |        2.177 |  2.92  |      0.004 |
| merges_prior_30m z              |      0.276 | 0.296 |        1.317 |  0.933 |      0.351 |


## Reading notes

- The git-augmented merge model should be read mainly as a sanity check that stale reconstruction signals add information beyond topic/file-touch labels.

- Very large negative merge coefficients for non-descendant/stale terms reflect the review process in this trace: reviewers often closed stale branches rather than rebasing them. That does not prove every stale branch was semantically unsafe.

- The keyword-risk model predicts comment labels, so it partly models reviewer attention and language rather than latent safety. Manual validation remains necessary.
