---
########### THIS FILE IS AUTO GENERATED - ANY CHANGES WILL BE VOID ###########
title: bigprints
description: OpenBB Telegram Command
---

# bigprints

This command allows the user to retrieve the last 15 large prints for a given cryptocurrency pair. The command uses the format "/crypto bigprints coin:BTC-USD" where BTC-USD is the currency pair for which the user wants to retrieve the large prints. This command is useful for analyzing the recent large prints of a given currency pair, which can be used to inform trading decisions.

### Usage

```python wordwrap
/bigprints coin [days]
```

---

## Parameters

| Name | Description | Optional | Choices |
| ---- | ----------- | -------- | ------- |
| coin | Coin to get prints for (e.g., btc) | False | ADA, AVAX, BTC, DAI, DOGE, DOT, ETH, LTC, MATIC, SHIB, SOL, TRX, USDC, USDT, WBTC, XRP |
| days | Number of days to get prints for (default: 10) | True | None |


---

## Examples

```
/bigprints ada
```

---
