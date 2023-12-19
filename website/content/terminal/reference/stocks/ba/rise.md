---
title: rise
description: The 'rise' is a command for printing top rising related queries of a
  specific stock. It sources its data from Google and is customizable based on user
  inputs, creating an efficient way of keeping track of specific stock metrics.
keywords:
- stocks
- stock metrics
- google sourced data
- top rising queries
- command line interface
- stock command
- query limit
---

import HeadTitle from '@site/src/components/General/HeadTitle.tsx';

<HeadTitle title="stocks/ba/rise - Reference | OpenBB Terminal Docs" />

Print top rising related queries with this stock's query. [Source: Google]

### Usage

```python
rise [-l LIMIT]
```

---

## Parameters

| Name | Description | Default | Optional | Choices |
| ---- | ----------- | ------- | -------- | ------- |
| limit | limit of top rising related queries to print. | 10 | True | None |


---

## Examples

```python
2022 Feb 16, 10:40 (🦋) /stocks/ba/ $ rise
Top rising AAPL's related queries
┏━━━━━━━━━━━━━━━━━┳━━━━━━━━┓
┃ query           ┃ value  ┃
┡━━━━━━━━━━━━━━━━━╇━━━━━━━━┩
│ nio stock       │ 227850 │
├─────────────────┼────────┤
│ nio             │ 183950 │
├─────────────────┼────────┤
│ pltr            │ 103100 │
├─────────────────┼────────┤
│ pltr stock      │ 82800  │
├─────────────────┼────────┤
│ mrna stock      │ 75050  │
├─────────────────┼────────┤
│ zm stock        │ 67850  │
├─────────────────┼────────┤
│ nio stock price │ 64000  │
├─────────────────┼────────┤
│ zm              │ 63500  │
├─────────────────┼────────┤
│ bynd            │ 61450  │
├─────────────────┼────────┤
│ bynd stock      │ 47450  │
└─────────────────┴────────┘
```
---
