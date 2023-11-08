---
title: cg
description: This document details the Center of Gravity indicator used to anticipate
  future price movements and to speculate the next price change of an asset, providing
  parameter descriptions, usage, and a demonstrative chart.
keywords:
- Center of Gravity
- COG
- price movements
- oscillator
- market trend
- price reversal
- asset price speculation
- technical analysis
---

import HeadTitle from '@site/src/components/General/HeadTitle.tsx';

<HeadTitle title="stocks/ta/cg - Reference | OpenBB Terminal Docs" />

The Center of Gravity indicator, in short, is used to anticipate future price movements and to trade on price reversals as soon as they happen. However, just like other oscillators, the COG indicator returns the best results in range-bound markets and should be avoided when the price is trending. Traders who use it will be able to closely speculate the upcoming price change of the asset.

### Usage

```python
cg [-l N_LENGTH]
```

---

## Parameters

| Name | Description | Default | Optional | Choices |
| ---- | ----------- | ------- | -------- | ------- |
| n_length | length | 14 | True | None |

![cg](https://user-images.githubusercontent.com/46355364/154310202-cd0d703e-21ba-41a2-b58a-5b8547efa887.png)

---
