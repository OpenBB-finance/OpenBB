---
title: rot
description: Rating over time (monthly)
keywords:
- stocks.fa
- rot
---

import HeadTitle from '@site/src/components/General/HeadTitle.tsx';

<HeadTitle title="stocks /fa/rot - Reference | OpenBB Terminal Docs" />

Rating over time (monthly). [Source: Finnhub]

### Usage

```python wordwrap
rot [-t TICKER] [-l LIMIT] [--raw]
```

---

## Parameters

| Name | Parameter | Description | Default | Optional | Choices |
| ---- | --------- | ----------- | ------- | -------- | ------- |
| ticker | -t  --ticker | Ticker to analyze | None | True | None |
| limit | -l  --limit | Limit of last months | 10 | True | None |
| raw | --raw | Only output raw data | False | True | None |

---
