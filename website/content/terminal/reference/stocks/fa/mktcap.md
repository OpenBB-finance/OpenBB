---
title: mktcap
description: The mktcap page describes the usage and parameters of the market cap
  estimate over time. The source for this data is Yahoo Finance. A Python line command
  is used to fetch and display this information.
keywords:
- mktcap
- market cap estimate
- Yahoo Finance
- python commands
- financial data
- parameters
- starting date
- data visualisation
---

import HeadTitle from '@site/src/components/General/HeadTitle.tsx';

<HeadTitle title="stocks /fa/mktcap - Reference | OpenBB Terminal Docs" />

Prints stock price, number of shares, market capitalization and enterprise value over time. The following fields are expected: Add total debt, Enterprise value, Market capitalization, Minus cash and cash equivalents, Number of shares, Stock price, and Symbol. [Source: Financial Modeling Prep]

### Usage

```python wordwrap
mktcap [-t TICKER] [-s START] [-e END] [-q] [-m {enterprise_value,market_cap}]
```

---

## Parameters

| Name | Parameter | Description | Default | Optional | Choices |
| ---- | --------- | ----------- | ------- | -------- | ------- |
| ticker | -t  --ticker | Ticker to analyze | None | True | None |
| start | -s  --start | The starting date (format YYYY-MM-DD) of the enterprise value to display. | 1900-01-01 | True | None |
| end | -e  --end | The ending date (format YYYY-MM-DD) of the enterprise value to display. | datetime.now() | True | None |
| b_quarter | -q  --quarter | Quarter fundamental data flag. | False | True | None |
| method | -m  --method | Define the data to display. | market_cap | True | enterprise_value, market_cap |

![gnus_mktcap](https://user-images.githubusercontent.com/25267873/156903038-46f46af1-68ca-435b-aed7-842da041864a.png)

---
