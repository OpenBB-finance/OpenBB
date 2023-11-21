---
title: chains
description: Detailed guide on how to display option chains with python usage. Documentation
  includes parameters for call options, put options, strike price, ask size, bid size,
  volume, open interest and others, along with their default values and options.
keywords:
- option chains
- parameters
- python usage
- call options
- put options
- strike price
- ask size
- bid size
- volume
- open interest
- delta
- gamma
- theta
- vega
- ask iv
- bid iv
- mid iv
---

import HeadTitle from '@site/src/components/General/HeadTitle.tsx';

<HeadTitle title="stocks/options/chains - Reference | OpenBB Terminal Docs" />

Display option chains

### Usage

```python
chains [-c] [-p] [-m MIN_SP] [-M MAX_SP] [-d TO_DISPLAY]
```

---

## Parameters

| Name | Description | Default | Optional | Choices |
| ---- | ----------- | ------- | -------- | ------- |
| calls | Flag to show calls only | False | True | None |
| puts | Flag to show puts only | False | True | None |
| min_sp | minimum strike price to consider. | -1 | True | None |
| max_sp | maximum strike price to consider. | -1 | True | None |
| to_display | (tradier only) Columns to look at. Columns can be: bid, ask, strike, bidsize, asksize, volume, open_interest, delta, gamma, theta, vega, ask_iv, bid_iv, mid_iv. E.g. 'bid,ask,strike' | mid_iv, vega, delta, gamma, theta, volume, open_interest, bid, ask | True | None |

---
