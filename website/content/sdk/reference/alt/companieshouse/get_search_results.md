---
title: get_search_results
description: All companies with searchStr in their name
keywords:
- alt
- companieshouse
- get_search_results
---

import HeadTitle from '@site/src/components/General/HeadTitle.tsx';

<HeadTitle title="alt.companieshouse.get_search_results - Reference | OpenBB SDK Docs" />

All companies with searchStr in their name.

Source Code: [[link](https://github.com/OpenBB-finance/OpenBBTerminal/tree/main/openbb_terminal/alternative/companieshouse/companieshouse_model.py#L23)]

```python wordwrap
openbb.alt.companieshouse.get_search_results(searchStr: str, limit: int = 20)
```

---

## Parameters

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| searchStr | str | The search string | None | False |
| limit | int | number of rows to return | 20 | True |


---

## Returns

| Type | Description |
| ---- | ----------- |
| pd.DataFrame | All comapanies with the search string in their name. |
---

## Examples

```python
from openbb_terminal.sdk import openbb
companies = openbb.alt.companieshouse.get_search_results("AstraZeneca")
```

---

