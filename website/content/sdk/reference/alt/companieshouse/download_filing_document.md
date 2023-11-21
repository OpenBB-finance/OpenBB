---
title: download_filing_document
description: Download company's filing document
keywords:
- alt
- companieshouse
- download_filing_document
---

import HeadTitle from '@site/src/components/General/HeadTitle.tsx';

<HeadTitle title="alt.companieshouse.download_filing_document - Reference | OpenBB SDK Docs" />

Download company's filing document.

Source Code: [[link](https://github.com/OpenBB-finance/OpenBBTerminal/tree/main/openbb_terminal/alternative/companieshouse/companieshouse_view.py#L188)]

```python wordwrap
openbb.alt.companieshouse.download_filing_document(company_number: str, company_name: str, transactionID: str, export: str = "")
```

---

## Parameters

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| company_number | str | company_number to retrieve filing history for | None | False |
| company_name | str | company_name to retrieve filing document for, this is used to name the downloaded file for easy access | None | False |
| transactionID | str | transaction id for filing | None | False |
| >>> companies = openbb.alt.companieshouse.get_search_results("AstraZeneca") | None |  | None | True |
| >>> openbb.alt.companieshouse.get_filing_document("02723534","AstraZeneca","MzM1NzQ0NzI5NWFkaXF6a2N4") | None |  | None | True |


---

## Returns

This function does not return anything

---

