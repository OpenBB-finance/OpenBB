---
title: cg
description: This page explains the use of the Center of Gravity (COG) indicator to
  anticipate future price movements and trade on price reversals. It also includes
  parameters and usage guide for COG indicator.
keywords:
- Center of Gravity indicator
- COG indicator
- future price movements
- trade on price reversals
- oscillators
- range-bound markets
- speculate upcoming price change
- CG parameters
- CG usage guide
- N_LENGTH
---

import HeadTitle from '@site/src/components/General/HeadTitle.tsx';

<HeadTitle title="crypto/ta/cg - Reference | OpenBB Terminal Docs" />

The Center of Gravity indicator, in short, is used to anticipate future price movements and to trade on price reversals as soon as they happen. However, just like other oscillators, the COG indicator returns the best results in range-bound markets and should be avoided when the price is trending. Traders who use it will be able to closely speculate the upcoming price change of the asset.

### Usage

```python
cg [-l N_LENGTH]
```

---

## Parameters

| Name | Description | Default | Optional | Choices |
| ---- | ----------- | ------- | -------- | ------- |
| n_length | length | 14 | True | range(1, 100) |

![cg](https://user-images.githubusercontent.com/46355364/154310202-cd0d703e-21ba-41a2-b58a-5b8547efa887.png)

---
