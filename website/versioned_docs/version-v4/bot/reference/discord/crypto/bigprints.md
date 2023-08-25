---
########### THIS FILE IS AUTO GENERATED - ANY CHANGES WILL BE VOID ###########
title: bigprints
description: OpenBB Discord Command
---

# bigprints

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
