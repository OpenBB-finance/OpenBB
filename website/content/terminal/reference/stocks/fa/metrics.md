---
title: metrics
description: This documentation page provides information on how to pull key metrics
  of a company over time using metrics command. Included data are Return on Equity
  (ROE), Working Capital, Current Ratio and Debt to Assets, among others.
keywords:
- metrics
- company metrics
- Return on Equity
- Working Capital
- Current Ratio
- Debt to Assets
- quarterly metrics
- annual metrics
- financial modeling
---

import HeadTitle from '@site/src/components/General/HeadTitle.tsx';

<HeadTitle title="stocks/fa/metrics - Reference | OpenBB Terminal Docs" />

Prints a list of the key metrics of a company over time. This can be either quarterly or annually. This includes, among other things, Return on Equity (ROE), Working Capital, Current Ratio and Debt to Assets. The following fields are expected: Average inventory, Average payables, Average receivables, Book value per share, Capex per share, Capex to depreciation, Capex to operating cash flow, Capex to revenue, Cash per share, Current ratio, Days of inventory on hand, Days payables outstanding, Days sales outstanding, Debt to assets, Debt to equity, Dividend yield, Earnings yield, Enterprise value, Enterprise value over EBITDA, Ev to free cash flow, Ev to operating cash flow, Ev to sales, Free cash flow per share, Free cash flow yield, Graham net net, Graham number, Income quality, Intangibles to total assets, Interest debt per share, Inventory turnover, Market cap, Net current asset value, Net debt to EBITDA, Net income per share, Operating cash flow per share, Payables turnover, Payout ratio, Pb ratio, Pe ratio, Pfcf ratio, Pocf ratio, Price to sales ratio, Ptb ratio, Receivables turnover, Research and development to revenue, Return on tangible assets, Revenue per share, Roe, Roic, Sales general and administrative to revenue, Shareholders equity per share, Stock based compensation to revenue, Tangible book value per share, and Working capital. [Source: Financial Modeling Prep]

### Usage

```python
metrics [-l LIMIT] [-q]
```

---

## Parameters

| Name | Description | Default | Optional | Choices |
| ---- | ----------- | ------- | -------- | ------- |
| limit | Limit of latest years/quarters. | 5 | True | None |
| b_quarter | Quarter fundamental data flag. | False | True | None |

---
