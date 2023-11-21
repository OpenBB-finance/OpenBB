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

<HeadTitle title="stocks /options/chains - Reference | OpenBB Terminal Docs" />

Display option chains

### Usage

```python wordwrap
chains [-c] [-p] [-m MIN_SP] [-M MAX_SP] [-d TO_DISPLAY] [-e {2023-11-24,2023-12-01,2023-12-08,2023-12-15,2023-12-22,2023-12-29,2024-01-19,2024-02-16,2024-03-15,2024-04-19,2024-06-21,2024-07-19,2024-09-20,2024-12-20,2025-01-17,2025-06-20,2025-09-19,2025-12-19,2026-01-16,}]
```

---

## Parameters

| Name | Parameter | Description | Default | Optional | Choices |
| ---- | --------- | ----------- | ------- | -------- | ------- |
| calls | -c  --calls | Flag to show calls only | False | True | None |
| puts | -p  --puts | Flag to show puts only | False | True | None |
| min_sp | -m  --min | minimum strike price to consider. | -1 | True | None |
| max_sp | -M  --max | maximum strike price to consider. | -1 | True | None |
| to_display | -d  --display | Columns to display | contractSymbol,optionType,expiration,strike,lastPrice,bid,ask,openInterest,volume,impliedVolatility | True | None |
| exp | -e  --expiration | Select expiration date (YYYY-MM-DD) |  | True | 2023-11-24, 2023-12-01, 2023-12-08, 2023-12-15, 2023-12-22, 2023-12-29, 2024-01-19, 2024-02-16, 2024-03-15, 2024-04-19, 2024-06-21, 2024-07-19, 2024-09-20, 2024-12-20, 2025-01-17, 2025-06-20, 2025-09-19, 2025-12-19, 2026-01-16,  |

---
