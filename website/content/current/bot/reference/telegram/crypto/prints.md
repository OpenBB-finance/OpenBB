---
title: prints
description: Documentation on the command allowing the user to retrieve the latest
  15 crypto prints for the specified coin over the last 24 hours. It includes information
  on the price, volume size, and other trading metrics.
keywords:
- Crypto Prints
- Bitcoin prints
- Ethereum prints
- Cryptocurrency tracking
- 24 hours cryptocurrency metrics
- Prints command
- Cryptocurrency trade volume
- Cryptocurrency price tracking
---

import HeadTitle from '@site/src/components/General/HeadTitle.tsx';

<HeadTitle title="crypto: prints - Telegram Reference | OpenBB Bot Docs" />

This command allows the user to retrieve the Last 15 Crypto Prints over the last 24 hours for the specified coin. The command will provide information on the price, volume, size, and other metrics associated with the prints.

### Usage

```python wordwrap
/prints coin
```

---

## Parameters

| Name | Description | Optional | Choices |
| ---- | ----------- | -------- | ------- |
| coin | Coin to get prints for (e.g., btc) | False | ADA, AVAX, BTC, DAI, DOGE, DOT, ETH, LTC, MATIC, SHIB, SOL, TRX, USDC, USDT, WBTC, XRP |


---

## Examples

```
/prints ada
```

---
