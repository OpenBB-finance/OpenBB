---
title: financials
description: This page provides information on the financials command which retrieves
  total assets, cash, debt, liabilities, and revenue of a company using its stock
  ticker. The data can be used to analyze a company's financial health.
keywords:
- financials
- total assets
- cash
- debt
- liabilities
- revenue
- company financial health
- stock
---

import HeadTitle from '@site/src/components/General/HeadTitle.tsx';

<HeadTitle title="duedilligence: financials - Discord Reference | OpenBB Bot Docs" />

This command will retrieve the financials of the company with the given ticker which includes total assets, cash, debt, liabilities, and revenue. This information can be used to analyze the financial health of the company.

### Usage

```python wordwrap
/dd financials ticker
```

---

## Parameters

| Name | Description | Optional | Choices |
| ---- | ----------- | -------- | ------- |
| ticker | Stock Ticker | False | None |


---

## Examples

```
/dd financials ticker:AMD
```
---
