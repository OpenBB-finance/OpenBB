---
title: ah
description: Documentation for the 'ah' command for retrieving afterhours data for
  a specific stock ticker, with usage, parameters, and examples.
keywords:
- Afterhours data
- Stock ticker
- Current stock price
- Highest and lowest prices
- Trade volume
- Market change
- Command usage
- Python command
---

import HeadTitle from '@site/src/components/General/HeadTitle.tsx';

<HeadTitle title="duedilligence: ah - Discord Reference | OpenBB Bot Docs" />

This command allows the user to retrieve afterhours data for a given stock ticker. The data retrieved will include the stock's current price, the highest and lowest prices of the ah session, the volume traded, and the change in the afterhours market.

### Usage

```python wordwrap
/dd ah ticker
```

---

## Parameters

| Name | Description | Optional | Choices |
| ---- | ----------- | -------- | ------- |
| ticker | Stock Ticker | False | None |


---

## Examples

```
/dd ah ticker:AMD
```
---
