---
title: rating
description: Based on specific ratios, prints information whether the company is a (strong) buy, neutral or a (strong) sell
keywords:
- stocks.fa
- rating
---

import HeadTitle from '@site/src/components/General/HeadTitle.tsx';

<HeadTitle title="stocks /fa/rating - Reference | OpenBB Terminal Docs" />

Based on specific ratios, prints information whether the company is a (strong) buy, neutral or a (strong) sell. The following fields are expected: P/B, ROA, DCF, P/E, ROE, and D/E. [Source: Financial Modeling Prep]

### Usage

```python wordwrap
rating [-t TICKER] [-l LIMIT]
```

---

## Parameters

| Name | Parameter | Description | Default | Optional | Choices |
| ---- | --------- | ----------- | ------- | -------- | ------- |
| ticker | -t  --ticker | Ticker to analyze | None | True | None |
| limit | -l  --limit | limit of last days to display ratings | 10 | True | None |

---
