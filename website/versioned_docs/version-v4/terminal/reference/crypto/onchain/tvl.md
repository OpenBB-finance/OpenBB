---
title: tvl
description: OpenBB Terminal Function
---

# tvl

Total value locked (TVL) metric - Ethereum ERC20 [Source:https://docs.flipsidecrypto.com/] useraddress OR addressname must be provided

### Usage

```python
tvl [-u USERADDRESS] [-a ADDRESSNAME] [-s SYMBOL] [-i INTERVAL]
```

---

## Parameters

| Name | Description | Default | Optional | Choices |
| ---- | ----------- | ------- | -------- | ------- |
| useraddress | User address we'd like to take a balance reading of against the contract | None | True | None |
| addressname | Address name corresponding to the user address | None | True | None |
| symbol | Contract symbol | USDC | True | None |
| interval | Interval in months | 12 | True | None |

---
