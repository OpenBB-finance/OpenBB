---
title: prices
description: This page provides information about displaying historical token prices.
  It includes parameters to sort data by date, cap, volumeConverted, open, high, close,
  and low values. The source of data is Ethplorer.
keywords:
- token prices
- historical prices
- Ethplorer
- date
- cap
- volumeConverted
- open
- high
- close
- low
- data sort
- ascending order
- descending order
---

import HeadTitle from '@site/src/components/General/HeadTitle.tsx';

<HeadTitle title="crypto/onchain/prices - Reference | OpenBB Terminal Docs" />

"Display token historical prices. e.g. 0x1f9840a85d5aF5bf1D1762F925BDADdC4201F984 [Source: Ethplorer]

### Usage

```python
prices [-l LIMIT] [-s {date,cap,volumeConverted,open,high,close,low}] [-r]
```

---

## Parameters

| Name | Description | Default | Optional | Choices |
| ---- | ----------- | ------- | -------- | ------- |
| limit | display N number records | 10 | True | None |
| sortby | Sort by given column. Default: date | date | True | date, cap, volumeConverted, open, high, close, low |
| reverse | Data is sorted in descending order by default. Reverse flag will sort it in an ascending way. Only works when raw data is displayed. | False | True | None |

---
