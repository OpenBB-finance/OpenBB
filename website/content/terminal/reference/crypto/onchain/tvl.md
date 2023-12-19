---
title: tvl
description: This page discusses the Total Value Locked (TVL) metric, a key concept
  in cryptocurrency. Learn how to utilize this metric through different parameters
  and understand its significance in evaluating Ethereum ERC20 contract balances.
keywords:
- Total Value Locked
- TVL
- Cryptocurrency
- Ethereum ERC20
- Contract balance
- User address
- Address name
- Contract symbol
- Interval
---

import HeadTitle from '@site/src/components/General/HeadTitle.tsx';

<HeadTitle title="crypto/onchain/tvl - Reference | OpenBB Terminal Docs" />

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
