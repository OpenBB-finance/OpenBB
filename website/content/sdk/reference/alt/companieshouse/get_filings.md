---
title: get_filings
description: Gets information on filings for given company, e
keywords:
- alt
- companieshouse
- get_filings
---

import HeadTitle from '@site/src/components/General/HeadTitle.tsx';

<HeadTitle title="alt.companieshouse.get_filings - Reference | OpenBB SDK Docs" />

Gets information on filings for given company, e.g. accounts, etc

Source Code: [[link](https://github.com/OpenBB-finance/OpenBBTerminal/tree/main/openbb_terminal/alternative/companieshouse/companieshouse_model.py#L252)]

```python wordwrap
openbb.alt.companieshouse.get_filings(company_number: str, category: str = "", start_index: Any = 0)
```

---

## Parameters

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| company_number | str | The company number.  Use get_search_results() to lookup company numbers. | None | False |


---

## Returns

| Type | Description |
| ---- | ----------- |
| pd.Dataframe | All information on all filings for company |
---

## Examples

```python
companies = openbb.alt.companieshouse.get_search_results("AstraZeneca")
signif_control_info = openbb.alt.companieshouse.get_filings("02723534")
```

---

