---
title: day
description: This documentation page provides detailed instructions on how to use
  the 'day' command to retrieve the most recent flow for a stock with a specified
  ticker symbol. It includes a description of optional and mandatory parameters and
  provides real-world usage examples.
keywords:
- stock market
- day command
- flow data
- ticker symbol
- expiry date
- strike price
- option type
- stock trading
- commands
- parameter
- examples
---

import HeadTitle from '@site/src/components/General/HeadTitle.tsx';

<HeadTitle title="flow: day - Discord Reference | OpenBB Bot Docs" />

This command retrieves the most recent flow for a stock with the specified ticker symbol. The command will return the most up-to-date flow data for that stock over $25,000.

### Usage

```python wordwrap
/flow day ticker [expiry] [strike] [opt_type]
```

---

## Parameters

| Name | Description | Optional | Choices |
| ---- | ----------- | -------- | ------- |
| ticker | Stock Ticker | False | None |
| expiry | Expiry Date (YYYY-MM-DD) (Optional) | True | None |
| strike | Strike Price (Optional) | True | None |
| opt_type | Option Type (Calls or Puts) (Optional) | True | Calls (C), Puts (P) |


---

## Examples

```
/flow day ticker:AMD
```

```
/flow day ticker:AMD expiry:2022-07-29 strike:60 opt_type:Puts
```

```
/flow day ticker:AMD expiry:2022-07-29 strike:60
```

---
