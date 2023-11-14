---
title: day
description: Information on how to use the 'flow' command to retrieve the most recent
  flow data for a stock. Learn how to specify the stock ticker, expiry date, strike
  price, and opt_type for more tailored results.
keywords:
- flow command
- stock flow data
- retrieve stock data
- stock ticker symbol
- expiration date
- strike price
- opt_type
- calls and puts
---

import HeadTitle from '@site/src/components/General/HeadTitle.tsx';

<HeadTitle title="flow - flow: day - Telegram Reference | OpenBB Bot Docs" />

This command retrieves the most recent flow for a stock with the specified ticker symbol. The command will return the most up-to-date flow data for that stock over $25,000.

### Usage

```python wordwrap
/flow [ticker] [expiry] [strike] [opt_type]
```

---

## Parameters

| Name | Description | Optional | Choices |
| ---- | ----------- | -------- | ------- |
| ticker | Stock Ticker - Not required for subcmd: unu | True | None |
| expiry | Expiration date - Only available for subcmd: day (default: None) | True | None |
| strike | Strike price - Only available for subcmd: day (default: None) | True | None |
| opt_type | call/put/calls/puts/c/p - Only available for subcmd: day (default: None) | True | Calls, Puts, c, p, call, put |


---

## Examples

```
/flow AMD
```

```
/flow AMD 2022-07-29
```

---
