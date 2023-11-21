---
title: get_persons_with_significant_control
description: Gets information on persons with significant control over the company
keywords:
- alt
- companieshouse
- get_persons_with_significant_control
---

import HeadTitle from '@site/src/components/General/HeadTitle.tsx';

<HeadTitle title="alt.companieshouse.get_persons_with_significant_control - Reference | OpenBB SDK Docs" />

Gets information on persons with significant control over the company

Source Code: [[link](https://github.com/OpenBB-finance/OpenBBTerminal/tree/main/openbb_terminal/alternative/companieshouse/companieshouse_model.py#L204)]

```python wordwrap
openbb.alt.companieshouse.get_persons_with_significant_control(company_number: str)
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
| pd.Dataframe | All persons with significant control over given company number |
---

## Examples

```python
companies = openbb.alt.companieshouse.get_search_results("AstraZeneca")
signif_control_info = openbb.alt.companieshouse.get_persons_with_significant_control("02723534")
```

---

