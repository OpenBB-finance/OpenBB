---
title: alldp
description: This page provides the 'alldp' command usage to retrieve the last 15
  darkpool trades for a specific stock ticker. It presents how to efficiently trade
  on a private stock trading system.
keywords:
- alldp command
- darkpool trades
- stock ticker
- private stock trading
- efficient trades
- retrieve trades
---

import HeadTitle from '@site/src/components/General/HeadTitle.tsx';

<HeadTitle title="darkpool: alldp - Discord Reference | OpenBB Bot Docs" />

This command allows the user to retrieve the last 15 darkpool trades for the specified stock ticker. A darkpool is a private stock trading system that allows large trades to take place without affecting the public market, providing access to larger and more efficient trades.

### Usage

```python wordwrap
/dp alldp ticker
```

---

## Parameters

| Name | Description | Optional | Choices |
| ---- | ----------- | -------- | ------- |
| ticker | Stock Ticker | False | None |


---

## Examples

```
/dp alldp ticker:AMD
```

---
