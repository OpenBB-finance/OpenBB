---
title: get_filing_document
description: Download given filing document pdf
keywords:
- alt
- companieshouse
- get_filing_document
---

import HeadTitle from '@site/src/components/General/HeadTitle.tsx';

<HeadTitle title="alt.companieshouse.get_filing_document - Reference | OpenBB SDK Docs" />

Download given filing document pdf

Source Code: [[link](https://github.com/OpenBB-finance/OpenBBTerminal/tree/main/openbb_terminal/alternative/companieshouse/companieshouse_model.py#L320)]

```python wordwrap
openbb.alt.companieshouse.get_filing_document(company_number: str, transactionID: str)
```

---

## Parameters

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| company_number | str | The company number.  Use get_search_results() to lookup company numbers. | None | False |
| transactionID | str | The filing transaction id. Use get_filings() to get id for each document | None | False |


---

## Returns

| Type | Description |
| ---- | ----------- |
| str | document category, e.g.confirmation-statement-with-updates, accounts-with-accounts-type-dormant, etc. |
---

## Examples

```python
companies = openbb.alt.companieshouse.get_search_results("AstraZeneca")
company_doc_info = openbb.alt.companieshouse.get_filing_document("02723534","MzM1NzQ0NzI5NWFkaXF6a2N4")
```

---

