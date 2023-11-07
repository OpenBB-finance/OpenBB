---
title: sec
description: The sec documentation page details how to use a feature for retrieving
  the latest SEC filings related to a specific ticker symbol. Information available
  includes company financials, registration statements, and periodic reports such
  as 10-Ks, 8-Ks, and 10-Qs. Useful for investors and analysts needing current data
  on a company's financial performance or other corporate documents.
keywords:
- sec command
- retrieve SEC filings
- financial performance
- corporate documents
- stock ticker
- company financials
- 10-Ks
- 8-Ks
- 10-Qs
- registration statements
- investors
- analysts
- periodic reports
---

import HeadTitle from '@site/src/components/General/HeadTitle.tsx';

<HeadTitle title="duedilligence: sec - Discord Reference | OpenBB Bot Docs" />

This command allows the user to retrieve the most recent SEC filings related to the specified ticker symbol. The filings can include company financials, registration statements, and periodic reports such as 10-Ks, 8-Ks, and 10-Qs. This command is especially useful for investors and analysts who need up-to-date information on a company's financial performance or other corporate documents.

### Usage

```python wordwrap
/dd sec ticker
```

---

## Parameters

| Name | Description | Optional | Choices |
| ---- | ----------- | -------- | ------- |
| ticker | Stock Ticker | False | None |


---

## Examples

```
/dd sec ticker:AMD
```
---
