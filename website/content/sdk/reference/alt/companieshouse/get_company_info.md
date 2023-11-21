---
title: get_company_info
description: Gets company info by company number
keywords:
- alt
- companieshouse
- get_company_info
---

import HeadTitle from '@site/src/components/General/HeadTitle.tsx';

<HeadTitle title="alt.companieshouse.get_company_info - Reference | OpenBB SDK Docs" />

Gets company info by company number

Source Code: [[link](https://github.com/OpenBB-finance/OpenBBTerminal/tree/main/openbb_terminal/alternative/companieshouse/companieshouse_model.py#L76)]

```python wordwrap
openbb.alt.companieshouse.get_company_info(company_number: str)
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
| str | Company address. |
---

## Examples

```python
companies = openbb.alt.companieshouse.get_search_results("AstraZeneca")
company_info = openbb.alt.companieshouse.get_company_info("02723534")
name = company_info.name
```

---

