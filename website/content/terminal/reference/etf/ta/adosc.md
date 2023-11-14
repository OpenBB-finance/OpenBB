---
title: adosc
description: Explore the Accumulation/Distribution Oscillator page, also known as
  the Chaikin Oscillator. This powerful momentum indicator analyzes the strength of
  price moves and the underlying buying and selling pressure in a given period. Learn
  how to use the indicator and understand its parameters like fast length and slow
  length.
keywords:
- Accumulation/Distribution Oscillator
- Chaikin Oscillator
- momentum indicator
- price moves
- buying pressure
- selling pressure
- market turning points
- adosc
- stock value
- fast length
- slow length
---

import HeadTitle from '@site/src/components/General/HeadTitle.tsx';

<HeadTitle title="etf/ta/adosc - Reference | OpenBB Terminal Docs" />

Accumulation/Distribution Oscillator, also known as the Chaikin Oscillator is essentially a momentum indicator, but of the Accumulation-Distribution line rather than merely price. It looks at both the strength of price moves and the underlying buying and selling pressure during a given time period. The oscillator reading above zero indicates net buying pressure, while one below zero registers net selling pressure. Divergence between the indicator and pure price moves are the most common signals from the indicator, and often flag market turning points.

### Usage

```python
adosc [--open] [--fast N_LENGTH_FAST] [--slow N_LENGTH_SLOW]
```

---

## Parameters

| Name | Description | Default | Optional | Choices |
| ---- | ----------- | ------- | -------- | ------- |
| b_use_open | uses open value of stock | False | True | None |
| n_length_fast | fast length | 3 | True | None |
| n_length_slow | slow length | 10 | True | None |

![adosc](https://user-images.githubusercontent.com/46355364/154309482-31c027ab-e80f-4145-9c63-392a74cf69c7.png)

---
