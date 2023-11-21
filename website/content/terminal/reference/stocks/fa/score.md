---
title: score
description: This is a documentation for Score, a Python command for a value investing
  tool based on insights by Warren Buffett, Joseph Piotroski, and Benjamin Graham.
  This command does not require any parameters.
keywords:
- Score
- Value Investing
- Warren Buffett
- Joseph Piotroski
- Benjamin Graham
- Investment tool
- FMP
- Python command
---

import HeadTitle from '@site/src/components/General/HeadTitle.tsx';

<HeadTitle title="stocks /fa/score - Reference | OpenBB Terminal Docs" />

Value investing based on Warren Buffett, Joseph Piotroski and Benjamin Graham thoughts [Source: FMP]. Data is gathered from fmp and the scores are calculated using the valinvest library. The repository For this library can be found here: https://github.com/astro30/valinvest

### Usage

```python wordwrap
score [-y YEARS] [-t TICKER]
```

---

## Parameters

| Name | Parameter | Description | Default | Optional | Choices |
| ---- | --------- | ----------- | ------- | -------- | ------- |
| years | -y  --years | Define the amount of years required to calculate the score. | 10 | True | None |
| ticker | -t  --ticker | Ticker to analyze | None | True | None |

---
