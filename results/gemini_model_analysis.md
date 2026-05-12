# Extended Gemini 3.1 Pro Analysis: heuristic predictors of PR success

This is a lightweight descriptive extension of the PR drift study, calculated without scikit-learn. It reports simple marginal merge rates, not a causal model and not manual safety adjudication.

## Likelihood of merge by categorical feature

**touch_main_js**:

- Present: 47.6% merged (n=456)

- Absent: 90.8% merged (n=153)

- Difference: -43.3%


**touch_anchorage**:

- Present: 96.1% merged (n=129)

- Absent: 48.3% merged (n=480)

- Difference: +47.8%


**title_cosmic_batch**:

- Present: 47.8% merged (n=441)

- Absent: 86.3% merged (n=168)

- Difference: -38.5%


**touch_config_js**:

- Present: 57.1% merged (n=7)

- Absent: 58.5% merged (n=602)

- Difference: -1.3%


**touch_landmark**:

- Present: 94.1% merged (n=135)

- Absent: 48.3% merged (n=474)

- Difference: +45.8%


**git_head_not_descendant_of_base**:

- Present: 1.4% merged (n=144)

- Absent: 76.1% merged (n=465)

- Difference: -74.7%


**git_touch_main_js**:

- Present: 47.4% merged (n=458)

- Absent: 92.1% merged (n=151)

- Difference: -44.7%


**git_touch_landmark**:

- Present: 62.1% merged (n=206)

- Absent: 56.6% merged (n=403)

- Difference: +5.6%


## GitHub API deletions: merge rates above simple thresholds

**deletions > 0**:

- > 0: 44.9% merged (n=216)

- <= 0: 65.9% merged (n=393)


**deletions > 5**:

- > 5: 48.4% merged (n=31)

- <= 5: 59.0% merged (n=578)


**deletions > 10**:

- > 10: 47.8% merged (n=23)

- <= 10: 58.9% merged (n=586)


**deletions > 50**:

- > 50: 41.2% merged (n=17)

- <= 50: 59.0% merged (n=592)


**deletions > 100**:

- > 100: 41.7% merged (n=12)

- <= 100: 58.8% merged (n=597)


## Git two-dot deletions: merge rates above simple thresholds

**git_deletions > 0**:

- > 0: 33.9% merged (n=289)

- <= 0: 80.6% merged (n=320)


**git_deletions > 10**:

- > 10: 7.2% merged (n=152)

- <= 10: 75.5% merged (n=457)


**git_deletions > 100**:

- > 100: 4.2% merged (n=118)

- <= 100: 71.5% merged (n=491)


**git_deletions > 1000**:

- > 1000: 16.7% merged (n=6)

- <= 1000: 58.9% merged (n=603)


**git_deletions > 10000**:

- > 10000: 0.0% merged (n=3)

- <= 10000: 58.7% merged (n=606)


## Stale-distance bins from local git

- 0 commits behind: 76.1% merged (n=465)

- 1 commit behind: 1.1% merged (n=93)

- 2-5 commits behind: 2.3% merged (n=44)

- 6-50 commits behind: 0.0% merged (n=4)

- >50 commits behind: 0.0% merged (n=3)



## Takeaways

- PRs touching `main.js` or having cosmic-batch titles were much less likely to merge in this trace, while landmark/Anchorage PRs had much higher merge rates. This supports treating shared-array batch edits and module-isolated landmark edits as separate regimes.

- Higher deletion thresholds correlate with lower merge rates, especially for local git two-dot deletions. This is consistent with H2, but it does not confirm H2 by itself because deletions can also reflect legitimate repair work and because merge outcome is not identical to semantic safety.

- Local git stale-distance features add a useful reconstruction layer: non-descendant heads and very large two-dot deletion counts are good audit-prioritization signals, but still require manual inspection.
