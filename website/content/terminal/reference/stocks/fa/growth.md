---
title: growth
description: This documentation page discusses the various parameters and functionalities
  of a financial growth model. It covers the growth of statement items and financial
  ratios, including revenue, operating cash flow, assets, debt, EBIT, EPS, gross profit,
  inventory, net income, operating income, and more. It provides usage examples and
  parameter descriptions using Financial Modeling Prep as the data source.
keywords:
- financial growth
- statement items growth
- financial ratios
- Revenue Growth
- inventory growth
- operating cash flow growth
- Asset growth
- Debt growth
- Ebit growth
- Eps growth
- Free cash flow growth
- Gross profit growth
- Inventory growth
- Net income growth
- Operating income growth
- Revenue growth
- Financial Modeling Prep
---

import HeadTitle from '@site/src/components/General/HeadTitle.tsx';

<HeadTitle title="stocks/fa/growth - Reference | OpenBB Terminal Docs" />

Prints the growth of several financial statement items and ratios over time. This can be either annually and quarterly. These are, among other things, Revenue Growth (3, 5 and 10 years), inventory growth and operating cash flow growth (3, 5 and 10 years). The following fields are expected: Asset growth, Book valueper share growth, Debt growth, Dividendsper share growth, Ebit growth, Eps diluted growth, Eps growth, Five y dividendper share growth per share, Five y net income growth per share, Five y operating c f growth per share, Five y revenue growth per share, Five y shareholders equity growth per share, Free cash flow growth, Gross profit growth, Inventory growth, Net income growth, Operating cash flow growth, Operating income growth, Rd expense growth, Receivables growth, Revenue growth, Sga expenses growth, Ten y dividendper share growth per share, Ten y net income growth per share, Ten y operating c f growth per share, Ten y revenue growth per share, Ten y shareholders equity growth per share, Three y dividendper share growth per share, Three y net income growth per share, Three y operating c f growth per share, Three y revenue growth per share, Three y shareholders equity growth per share, Weighted average shares diluted growth, and Weighted average shares growth [Source: Financial Modeling Prep]

### Usage

```python
growth [-l LIMIT] [-q]
```

---

## Parameters

| Name | Description | Default | Optional | Choices |
| ---- | ----------- | ------- | -------- | ------- |
| limit | Limit of latest years/quarters. | 5 | True | None |
| b_quarter | Quarter fundamental data flag. | False | True | None |

---
