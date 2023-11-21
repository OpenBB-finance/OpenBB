---
title: chains
description: This docusaurus page explores the `chains` command which allows users
  to view Options Chains by Expiry for a specific stock. It also explains several
  parameters such as Stock Ticker, Expiration Date, type of options Calls
  or Puts, and Strike Prices.
keywords:
- Options Chains by Expiry
- Stock Ticker
- Expiration Date
- Calls or Puts
- Minimum Strike Price
- Maximum Strike Price
---

import HeadTitle from '@site/src/components/General/HeadTitle.tsx';

<HeadTitle title="options: chains - Discord Reference | OpenBB Bot Docs" />

This command allows users to retrieve Options Chain by Expiry, which gives an overview of the bid, ask, and open interest of options contracts for a specific stock.

### Usage

```python wordwrap
/op chains ticker expiry opt_type [min_sp] [max_sp]
```

---

## Parameters

| Name | Description | Optional | Choices |
| ---- | ----------- | -------- | ------- |
| ticker | Stock Ticker | False | None |
| expiry | Expiration Date | False | None |
| opt_type | Calls or Puts | False | Calls, Puts |
| min_sp | Minimum Strike Price | True | None |
| max_sp | Maximum Strike Price | True | None |


---

## Examples

```
/op chains ticker:AMD expiry:2022-07-29 opt_type:Calls
```

```
/op chains ticker:AMD expiry:2022-07-29 opt_type:Calls min_sp:10 max_sp:100
```

---
