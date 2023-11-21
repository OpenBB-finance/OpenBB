---
title: get_officers
description: Gets information on company officers
keywords:
- alt
- companieshouse
- get_officers
---

import HeadTitle from '@site/src/components/General/HeadTitle.tsx';

<HeadTitle title="alt.companieshouse.get_officers - Reference | OpenBB SDK Docs" />

Gets information on company officers

Source Code: [[link](https://github.com/OpenBB-finance/OpenBBTerminal/tree/main/openbb_terminal/alternative/companieshouse/companieshouse_model.py#L156)]

```python wordwrap
openbb.alt.companieshouse.get_officers(company_number: str)
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
| pd.Dataframe | All officers for given company number |
---

## Examples

```python
companies = openbb.alt.companieshouse.get_search_results("AstraZeneca")
officer_info = openbb.alt.companieshouse.get_officers("02723534")
```

---

