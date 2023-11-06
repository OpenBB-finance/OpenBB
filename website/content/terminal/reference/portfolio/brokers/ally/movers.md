---
title: movers
description: This documentation page provides information on how to get stock movers
  using Python command line. Detailed explanations for different parameters such as
  list_type, exchange, and limit are included.
keywords:
- stock movers
- Python command line
- list_type parameter
- exchange parameter
- limit parameter
- toplosers
- toppctlosers
- topvolume
- topactive
- topgainers
- toppctgainers
- American Stock Exchange
- New York Stock Exchange
- NASDAQ
---

import HeadTitle from '@site/src/components/General/HeadTitle.tsx';

<HeadTitle title="portfolio/ally/movers /brokers - Reference | OpenBB Terminal Docs" />

Get stock movers

### Usage

```python
movers [-t {toplosers,toppctlosers,topvolume,topactive,topgainers,toppctgainers}] [-e {A,N,Q,U,V}] [-l LIMIT]
```

---

## Parameters

| Name | Description | Default | Optional | Choices |
| ---- | ----------- | ------- | -------- | ------- |
| list_type | List to get movers of | topactive | True | toplosers, toppctlosers, topvolume, topactive, topgainers, toppctgainers |
| exchange | Exchange to look at. Can be A:American Stock Exchange. N:New York Stock Exchange. Q:NASDAQ U:NASDAQ Bulletin Board V:NASDAQ OTC Other | N | True | A, N, Q, U, V |
| limit | Number to show | 15 | True | None |

---
