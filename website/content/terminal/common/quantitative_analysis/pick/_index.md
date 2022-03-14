```text
usage: pick [-t {Open,High,Low,Close,AdjClose,Volume,Returns,LogRet}] [-h]
```
Select a target variable from the available arguments listed.

```
optional arguments:
  -t {Open,High,Low,Close,AdjClose,Volume,Returns,LogRet}, --target {Open,High,Low,Close,AdjClose,Volume,Returns,LogRet}
                        Select variable to analyze (default: None)
  -h, --help            show this help message (default: False)
```

Example:
```
2022 Feb 16, 11:12 (✨) /stocks/qa/ $ load tsla

Loading Daily TSLA stock with starting period 2019-02-11 for analysis.

Datetime: 2022 Feb 16 11:12
Timezone: America/New_York
Currency: USD
Market:   CLOSED


2022 Feb 16, 11:12 (✨) /stocks/qa/ $ pick adjclose
```
