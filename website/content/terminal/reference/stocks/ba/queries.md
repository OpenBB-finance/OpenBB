---
title: queries
description: This page provides documentation on how to use the 'queries' function
  to print the top related queries associated with a stock's query. Learn how to set
  a limit on the number of queries and view examples of the output.
keywords:
- stock
- query
- stock query
- top related queries
- print
- stock's query
- function
- Google source
- limit
- parameters
- examples
- output
---

import HeadTitle from '@site/src/components/General/HeadTitle.tsx';

<HeadTitle title="stocks/ba/queries - Reference | OpenBB Terminal Docs" />

Print top related queries with this stock's query. [Source: Google]

### Usage

```python
queries [-l LIMIT]
```

---

## Parameters

| Name | Description | Default | Optional | Choices |
| ---- | ----------- | ------- | -------- | ------- |
| limit | limit of top related queries to print. | 10 | True | None |


---

## Examples

```python
2022 Feb 16, 10:38 (🦋) /stocks/ba/ $ queries
 Top AMZN's related queries
┏━━━━━━━━━━━━━━━━━━┳━━━━━━━┓
┃ query            ┃ value ┃
┡━━━━━━━━━━━━━━━━━━╇━━━━━━━┩
│ amzn stock       │ 100%  │
├──────────────────┼───────┤
│ amzn price       │ 31%   │
├──────────────────┼───────┤
│ amzn stock price │ 26%   │
├──────────────────┼───────┤
│ aapl             │ 25%   │
├──────────────────┼───────┤
│ tsla             │ 18%   │
├──────────────────┼───────┤
│ aapl stock       │ 15%   │
├──────────────────┼───────┤
│ fb stock         │ 12%   │
├──────────────────┼───────┤
│ msft             │ 12%   │
├──────────────────┼───────┤
│ tsla stock       │ 12%   │
├──────────────────┼───────┤
│ goog             │ 9%    │
└──────────────────┴───────┘
```
---
