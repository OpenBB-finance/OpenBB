---
title: divs
description: This documentation page provides explanation about the usage, and parameters
  of the 'divs' function in showing historical dividends of a company.
keywords:
- divs function
- historical dividends
- dividend plotting
- function parameters
- dividend history
---

import HeadTitle from '@site/src/components/General/HeadTitle.tsx';

<HeadTitle title="stocks /fa/divs - Reference | OpenBB Terminal Docs" />

Historical dividends for a company

### Usage

```python wordwrap
divs [-t TICKER] [-l LIMIT] [-p]
```

---

## Parameters

| Name | Parameter | Description | Default | Optional | Choices |
| ---- | --------- | ----------- | ------- | -------- | ------- |
| ticker | -t  --ticker | Ticker to analyze | None | True | None |
| limit | -l  --limit | Number of previous dividends to show | 16 | True | None |
| plot | -p  --plot | Plots changes in dividend over time | False | True | None |

---
