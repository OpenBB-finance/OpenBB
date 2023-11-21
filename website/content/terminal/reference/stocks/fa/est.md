---
title: est
description: Yearly estimates and quarter earnings/revenues
keywords:
- stocks.fa
- est
---

import HeadTitle from '@site/src/components/General/HeadTitle.tsx';

<HeadTitle title="stocks /fa/est - Reference | OpenBB Terminal Docs" />

Yearly estimates and quarter earnings/revenues. [Source: Business Insider]

### Usage

```python wordwrap
est [-t TICKER] [-e {annual_earnings,quarter_earnings,quarter_revenues}]
```

---

## Parameters

| Name | Parameter | Description | Default | Optional | Choices |
| ---- | --------- | ----------- | ------- | -------- | ------- |
| ticker | -t  --ticker | Ticker to analyze | None | True | None |
| estimate | -e  --estimate | Estimates to get | annual_earnings | True | annual_earnings, quarter_earnings, quarter_revenues |

---
