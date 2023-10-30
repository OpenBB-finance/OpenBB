---
title: rating
description: A page detailing the rating system for evaluating companies based on
  specific financial ratios. It prints information on whether a company is a buy,
  neutral or sell. This page provides usage details and parameters for obtaining ratings.
keywords:
- Rating
- Company Evaluation
- Buy or Sell Recommendation
- Financial Ratios
- P/B
- ROA
- DCF
- P/E
- ROE
- D/E
- Financial Modeling Prep
- Limit
- Last Days Ratings
---

import HeadTitle from '@site/src/components/General/HeadTitle.tsx';

<HeadTitle title="stocks/dd/rating - Reference | OpenBB Terminal Docs" />

Based on specific ratios, prints information whether the company is a (strong) buy, neutral or a (strong) sell. The following fields are expected: P/B, ROA, DCF, P/E, ROE, and D/E. [Source: Financial Modeling Prep]

### Usage

```python
rating [-l LIMIT]
```

---

## Parameters

| Name | Description | Default | Optional | Choices |
| ---- | ----------- | ------- | -------- | ------- |
| limit | limit of last days to display ratings | 10 | True | None |

---
