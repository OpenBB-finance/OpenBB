```
usage: fraud [-h] [--export {csv,json,xlsx}]
```

```
optional arguments:
  -e, --explanation     whether to show the description for the metrics (default: false)
  -h, --help            show this help message
  --export {csv,json,xlsx}
                        Export raw data into csv, json, xlsx
```

Example (ticker is MSFT):
```
2022 Feb 16, 05:42 (✨) /stocks/fa/ $ fraud
AMscore Sub Stats:
   DSRI : 1.03
   GMI : 0.98
   AQI : 0.50
   SGI : 1.18
   DEPI : 1.07
   SGAI : 0.86
   LVGI : 0.95
   TATA : -0.05

MSCORE:  -2.62 (low chance of fraud)
ZSCORE:  -1.89 (high chance of bankruptcy)

McKee:  0.86 (high chance of bankruptcy)
```

Mscore:
------------------------------------------------
The Beneish model is a statistical model that uses financial ratios calculated with accounting data of a specific company in order to check if it is likely (high probability) that the reported earnings of the company have been manipulated. A score of -5 to -2.22 indicated a low chance of fraud, a score of -2.22 to -1.78 indicates a moderate change of fraud, and a score above -1.78 indicated a high chance of fraud.[Source: Wikipedia]

DSRI:
Days Sales in Receivables Index gauges whether receivables and revenue are out of balance, a large number is expected to be associated with a higher likelihood that revenues and earnings are overstated.

GMI:
Gross Margin Index shows if gross margins are deteriorating. Research suggests that firms with worsening gross margin are more likely to engage in earnings management, therefore there should be a positive correlation between GMI and probability of earnings management.

AQI:
Asset Quality Index measures the proportion of assets where potential benefit is less certain. A positive relation between AQI and earnings manipulation is expected.

SGI:
Sales Growth Index shows the amount of growth companies are having. Higher growth companies are more likely to commit fraud so there should be a positive relation between SGI and earnings management.

DEPI:
Depreciation Index is the ratio for the rate of depreciation. A DEPI greater than 1 shows that the depreciation rate has slowed and is positively correlated with earnings management.

SGAI:
Sales General and Administrative Expenses Index measures the change in SG&A over sales. There should be a positive relationship between SGAI and earnings management.

LVGI:
Leverage Index represents change in leverage. A LVGI greater than one indicates a lower change of fraud.

TATA:
Total Accruals to Total Assets is a proxy for the extent that cash underlies earnigns. A higher number is associated with a higher likelihood of manipulation.

Zscore:
------------------------------------------------
The Zmijewski Score is a bankruptcy model used to predict a firm's bankruptcy in two years. The ratio uses in the Zmijewski score were determined by probit analysis (think of probit as probability unit). In this case, scores less than .5 represent a higher probability of default. One of the criticisms that Zmijewski made was that other bankruptcy scoring models oversampled distressed firms and favored situations with more complete data.[Source: YCharts]

McKee Score:
------------------------------------------------
The McKee Score is a bankruptcy model used to predict a firm's bankruptcy in one year. It looks at a companie's size, profitability, and liquidity to determine the probability. This model is 80% accurate in predicting bankruptcy.
[Source: McKee and Lensberg](https://citeseerx.ist.psu.edu/viewdoc/download?doi=10.1.1.619.594&rep=rep1&type=pdf)
