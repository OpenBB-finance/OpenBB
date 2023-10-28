---
title: ds
description: DS provides daily transactions of certain symbols in Ethereum blockchain,
  it supports platforms such as uniswap-v3, uniswap-v2, sushiswap, and curve. It primarily
  helps in checking fees and the number of users over time.
keywords:
- ds
- daily transactions
- ethereum blockchain
- platforms
- uniswap-v3
- uniswap-v2
- sushiswap
- curve
- fees
- number of users over time
---

import HeadTitle from '@site/src/components/General/HeadTitle.tsx';

<HeadTitle title="crypto/onchain/ds - Reference | OpenBB Terminal Docs" />

Get daily transactions for certain symbols in ethereum blockchain [Source: https://sdk.flipsidecrypto.xyz/shroomdk]

### Usage

```python
ds [-p {uniswap-v3,uniswap-v2,sushiswap,curve}]
```

---

## Parameters

| Name | Description | Default | Optional | Choices |
| ---- | ----------- | ------- | -------- | ------- |
| platform | Ethereum platform to check fees/number of users over time | curve | True | uniswap-v3, uniswap-v2, sushiswap, curve |

---
