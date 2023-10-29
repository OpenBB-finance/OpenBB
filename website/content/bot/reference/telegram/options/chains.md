---
title: chains
description: This documentation page is about the /chains command, which helps users
  retrieve Options Chain by Expiry. This crucial tool provides an overview of the
  bid, ask, and open interest of options contracts for a specific stock.
keywords:
- chains command
- Options Chain by Expiry
- bid
- ask
- open interest
- stock options contracts
- stock ticker
- expiration date
- calls or puts
- strike price
---

import HeadTitle from '@site/src/components/General/HeadTitle.tsx';

<HeadTitle title="options: chains - Telegram Reference | OpenBB Bot Docs" />

This command allows users to retrieve Options Chain by Expiry, which gives an overview of the bid, ask, and open interest of options contracts for a specific stock.

### Usage

```python wordwrap
/chains ticker expiry opt_type [min_sp] [max_sp]
```

---

## Parameters

| Name | Description | Optional | Choices |
| ---- | ----------- | -------- | ------- |
| ticker | Stock Ticker | False | None |
| expiry | Expiration Date (YYYY-MM-DD) | False | None |
| opt_type | Calls or Puts (C or P) | False | calls, puts, C, P |
| min_sp | Minimum Strike Price | True | None |
| max_sp | Maximum Strike Price | True | None |


---

## Examples

```
/chains AMD 2022-07-29 Calls
```
```
/chains AMD 2022-07-29 Calls 10 100
```

---
