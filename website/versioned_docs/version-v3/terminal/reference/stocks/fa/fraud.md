---
title: fraud
description: OpenBB Terminal Function
---

# fraud

M-score: ------------------------------------------------ The Beneish model is a statistical model that uses financial ratios calculated with accounting data of a specific company in order to check if it is likely (high probability) that the reported earnings of the company have been manipulated. A score of -5 to -2.22 indicated a low chance of fraud, a score of -2.22 to -1.78 indicates a moderate change of fraud, and a score above -1.78 indicated a high chance of fraud.[Source: Wikipedia] DSRI: Days Sales in Receivables Index gauges whether receivables and revenue are out of balance, a large number is expected to be associated with a higher likelihood that revenues and earnings are overstated. GMI: Gross Margin Index shows if gross margins are deteriorating. Research suggests that firms with worsening gross margin are more likely to engage in earnings management, therefore there should be a positive correlation between GMI and probability of earnings management. AQI: Asset Quality Index measures the proportion of assets where potential benefit is less certain. A positive relation between AQI and earnings manipulation is expected. SGI: Sales Growth Index shows the amount of growth companies are having. Higher growth companies are more likely to commit fraud so there should be a positive relation between SGI and earnings management. DEPI: Depreciation Index is the ratio for the rate of depreciation. A DEPI greater than 1 shows that the depreciation rate has slowed and is positively correlated with earnings management. SGAI: Sales General and Administrative Expenses Index measures the change in SG&A over sales. There should be a positive relationship between SGAI and earnings management. LVGI: Leverage Index represents change in leverage. A LVGI greater than one indicates a lower change of fraud. TATA: Total Accruals to Total Assets is a proxy for the extent that cash underlies earnings. A higher number is associated with a higher likelihood of manipulation. Z-score: ------------------------------------------------ The Zmijewski Score is a bankruptcy model used to predict a firm's bankruptcy in two years. The ratio uses in the Zmijewski score were determined by probit analysis (think of probit as probability unit). In this case, scores less than .5 represent a higher probability of default. One of the criticisms that Zmijewski made was that other bankruptcy scoring models oversampled distressed firms and favored situations with more complete data.[Source: YCharts] McKee-score: ------------------------------------------------ The McKee Score is a bankruptcy model used to predict a firm's bankruptcy in one yearIt looks at a company's size, profitability, and liquidity to determine the probability.This model is 80% accurate in predicting bankruptcy.

### Usage

```python
fraud [-e] [-d]
```

---

## Parameters

| Name | Description | Default | Optional | Choices |
| ---- | ----------- | ------- | -------- | ------- |
| exp | Shows an explanation for the metrics | False | True | None |
| detail | Shows the details for calculating the mscore | False | True | None |

---
