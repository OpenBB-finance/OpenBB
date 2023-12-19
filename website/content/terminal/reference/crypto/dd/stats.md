---
title: stats
description: The 'stats' page provides 24 hour statistical data on cryptocurrencies
  with options to view data in various quote currencies. It displays metrics such
  as open value, high, low, volume, and last known value.
keywords:
- coin stats
- crypto stats
- quote currency
- 24 hr Product Stats
- USD
- USDC
- USDT
- EUR
- GBP
- volume
- open
- high
- low
- last
- volume_30day
---

import HeadTitle from '@site/src/components/General/HeadTitle.tsx';

<HeadTitle title="crypto/dd/stats - Reference | OpenBB Terminal Docs" />

Display coin stats

### Usage

```python
stats [--vs {USD,USDC,USDT,EUR,USD,GBP}]
```

---

## Parameters

| Name | Description | Default | Optional | Choices |
| ---- | ----------- | ------- | -------- | ------- |
| vs | Quote currency (what to view coin vs) | USDT | True | USD, USDC, USDT, EUR, USD, GBP |


---

## Examples

```python
2022 Feb 15, 07:47 (🦋) /crypto/dd/ $ stats

       24 hr Product Stats
┌──────────────┬────────────────┐
│ Metric       │ Value          │
├──────────────┼────────────────┤
│ open         │ 42551.99       │
├──────────────┼────────────────┤
│ high         │ 44428.47       │
├──────────────┼────────────────┤
│ low          │ 41800          │
├──────────────┼────────────────┤
│ volume       │ 743.03129474   │
├──────────────┼────────────────┤
│ last         │ 44183.84       │
├──────────────┼────────────────┤
│ volume_30day │ 22665.06104665 │
└──────────────┴────────────────┘
```
---
