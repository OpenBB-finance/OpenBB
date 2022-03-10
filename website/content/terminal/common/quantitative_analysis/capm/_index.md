```text
usage: capm [-h]
```

Provides detailed information about a stock's risk compared to the market risk.

```
optional arguments:
  -h, --help            show this help message (default: False)
```

Example:
```
2022 Feb 16, 11:01 (✨) /stocks/qa/ $ load tsla

Loading Daily TSLA stock with starting period 2019-02-11 for analysis.

Datetime: 2022 Feb 16 11:02
Timezone: America/New_York
Currency: USD
Market:   CLOSED


2022 Feb 16, 11:02 (✨) /stocks/qa/ $ capm
Beta:                   2.02
Systematic Risk:        23.09%
Unsystematic Risk:      76.91%
```
