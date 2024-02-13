---
title: filings
description: Select the company number to retrieve filling history for
keywords:
- alt.companieshouse
- filings
---

import HeadTitle from '@site/src/components/General/HeadTitle.tsx';

<HeadTitle title="alt /companieshouse/filings - Reference | OpenBB Terminal Docs" />

Select the company number to retrieve filling history for. [Source: UK Companies House]

### Usage

```python wordwrap
filings [-k category] [-l limit]
```

---

## Parameters

| Name | Parameter | Description | Default | Optional | Choices |
| ---- | --------- | ----------- | ------- | -------- | ------- |
| category | -k  --category | category | None | True | accounts, address, capital, incorporation, officers, resolution |
| limit | -l  --limit | Number of entries to return | 100 | True | None |

---
