---
title: bigprints
description: The documentation page explains the '/crypto bigprints coin:BTC-USD'
  command which retrieves last 15 large cryptocurrency prints. Informative for trading
  decisions.
keywords:
- Cryptocurrency
- Crypto Trading
- Trading decisions
- Command documentation
- Crypto bigprints
- BTC-USD
- Currency pair
- Large crypto prints
---

import HeadTitle from '@site/src/components/General/HeadTitle.tsx';

<HeadTitle title="crypto: bigprints - Discord Reference | OpenBB Bot Docs" />

This command allows the user to retrieve the last 15 large prints for a given cryptocurrency pair. The command uses the format "/crypto bigprints coin:BTC-USD" where BTC-USD is the currency pair for which the user wants to retrieve the large prints. This command is useful for analyzing the recent large prints of a given currency pair, which can be used to inform trading decisions.

### Usage

```python wordwrap
/crypto bigprints coin [days]
```

---

## Parameters

| Name | Description | Optional | Choices |
| ---- | ----------- | -------- | ------- |
| coin | Coin from the list of supported coins | False | ADA-USD, AVAX-USD, BTC-USD, DAI-USD, DOGE-USD, DOT-USD, ETH-USD, LTC-USD, MATIC-USD, SHIB-USD, SOL-USD, TRX-USD, USDC-USD, USDT-USD, WBTC-USD, XRP-USD |
| days | Number of days to look back. Default is 10. | True | None |


---

## Examples

```
/crypto bigprints coin:BTC-USD
```

---
