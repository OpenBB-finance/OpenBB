---
title: FILINGS
description: Get the most-recent filings submitted to the SEC
keywords: 
- equity
- discovery
- filings
---

<!-- markdownlint-disable MD033 -->
import HeadTitle from '@site/src/components/General/HeadTitle.tsx';

<HeadTitle title="EQUITY.DISCOVERY.FILINGS | OpenBB Add-in for Excel Docs" />

Get the most-recent filings submitted to the SEC.

## Syntax

```excel wordwrap
=OBB.EQUITY.DISCOVERY.FILINGS([start_date];[end_date];[form_type];[limit];[provider];[isDone])
```

### Example

```excel wordwrap
=OBB.EQUITY.DISCOVERY.FILINGS()
```

---

## Parameters

| Name | Type | Description | Required |
| ---- | ---- | ----------- | -------- |
| start_date | Text | Start date of the data, in YYYY-MM-DD format. | False |
| end_date | Text | End date of the data, in YYYY-MM-DD format. | False |
| form_type | Text | Filter by form type. Visit https://www.sec.gov/forms for a list of supported form types. | False |
| limit | Number | The number of data entries to return. | False |
| provider | Text | Options: fmp, defaults to fmp. | False |
| isDone | Boolean | Flag for whether or not the filing is done. (provider: fmp) | False |

---

## Return Data

| Name | Description |
| ---- | ----------- |
| symbol | Symbol representing the entity requested in the data.  |
| cik | Central Index Key (CIK) for the requested entity.  |
| title | Title of the filing.  |
| date | The date of the data.  |
| form_type | The form type of the filing  |
| link | URL to the filing page on the SEC site.  |
