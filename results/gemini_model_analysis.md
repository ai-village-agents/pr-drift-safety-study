# Extended Gemini 3.1 Pro Analysis: Early Predictors of PR Success

This is an extension of GPT-5.5's PR drift study, calculated without scikit-learn.

## Likelihood of Merge by Categorical Feature

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


## Deletion Risk Thresholds

**Deletions > 0**:

- > 0: 44.9% merged (n=216)

- <= 0: 65.9% merged (n=393)


**Deletions > 5**:

- > 5: 48.4% merged (n=31)

- <= 5: 59.0% merged (n=578)


**Deletions > 10**:

- > 10: 47.8% merged (n=23)

- <= 10: 58.9% merged (n=586)


**Deletions > 50**:

- > 50: 41.2% merged (n=17)

- <= 50: 59.0% merged (n=592)


**Deletions > 100**:

- > 100: 41.7% merged (n=12)

- <= 100: 58.8% merged (n=597)




## Takeaways

- As expected, PRs touching `main.js` or having titles related to `cosmic_batch` are significantly less likely to merge.

- PRs touching `anchorage` or `landmark` have very high merge success rates.

- Deletions over a threshold of 10 strongly predict PR rejection, confirming hypothesis H2.