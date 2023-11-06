---
title: ratios
description: A comprehensive guide on using the 'ratios' function. It offers an in-depth
  analysis of a company's ratios over time, which includes financial metrics like
  Payout Ratio, Price-to-Book Ratio, Debt equity ratio, Dividend payout ratio and
  much more.
keywords:
- ratios
- financial ratios
- debt equity ratio
- dividend payout ratio
- price to book ratio
- financial modeling
- asset turnover
- cash flow
- return on equity
- operating cycle
---

import HeadTitle from '@site/src/components/General/HeadTitle.tsx';

<HeadTitle title="stocks/fa/ratios - Reference | OpenBB Terminal Docs" />

Prints in-depth ratios of a company over time. This can be either quarterly or annually. This contains, among other things, Price-to-Book Ratio, Payout Ratio and Operating Cycle. The following fields are expected: Asset turnover, Capital expenditure coverage ratio, Cash conversion cycle, Cash flow coverage ratios, Cash flow to debt ratio, Cash per share, Cash ratio, Company equity multiplier, Current ratio, Days of inventory outstanding, Days of payables outstanding, Days of sales outstanding, Debt equity ratio, Debt ratio, Dividend paid and capex coverage ratio, Dividend payout ratio, Dividend yield, Ebit per revenue, Ebt per ebit, Effective tax rate, Enterprise value multiple, Fixed asset turnover, Free cash flow operating cash flow ratio, Free cash flow per share, Gross profit margin, Inventory turnover, Long term debt to capitalization, Net income per EBT, Net profit margin, Operating cash flow per share, Operating cash flow sales ratio, Operating cycle, Operating profit margin, Payables turnover, Payout ratio, Pretax profit margin, Price book value ratio, Price cash flow ratio, Price earnings ratio, Price earnings to growth ratio, Price fair value, Price sales ratio, Price to book ratio, Price to free cash flows ratio, Price to operating cash flows ratio, Price to sales ratio, Quick ratio, Receivables turnover, Return on assets, Return on capital employed, Return on equity, Short term coverage ratios, and Total debt to capitalization. [Source: Financial Modeling Prep]

### Usage

```python
ratios [-l LIMIT] [-q]
```

---

## Parameters

| Name | Description | Default | Optional | Choices |
| ---- | ----------- | ------- | -------- | ------- |
| limit | Limit of latest years/quarters. | 5 | True | None |
| b_quarter | Quarter fundamental data flag. | False | True | None |

---
