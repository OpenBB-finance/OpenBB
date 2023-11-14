---
title: dcfc
description: This page provides instructions on how to use the 'dcfc' function to
  extract a company's discounted cash flow (DCF), stock price, and date information.
  It further provides details on usage and parameters.
keywords:
- dcfc
- discounted cash flow
- stock price
- financial data extraction
- financial modeling
- DCF
- quarters
- fundamental data
---

import HeadTitle from '@site/src/components/General/HeadTitle.tsx';

<HeadTitle title="stocks/fa/dcfc - Reference | OpenBB Terminal Docs" />

Prints the discounted cash flow of a company over time including the DCF of today. The following fields are expected: DCF, Stock price, and Date. [Source: Financial Modeling Prep]

### Usage

```python
dcfc [-l LIMIT] [-q]
```

---

## Parameters

| Name | Description | Default | Optional | Choices |
| ---- | ----------- | ------- | -------- | ------- |
| limit | Limit of latest years/quarters. | 5 | True | None |
| b_quarter | Quarter fundamental data flag. | False | True | None |

---
