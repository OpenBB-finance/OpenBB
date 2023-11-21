---
title: icebofa
description: Get data for ICE BofA US Corporate Bond Indices
keywords:
- fixedincome
- icebofa
---

import HeadTitle from '@site/src/components/General/HeadTitle.tsx';

<HeadTitle title="fixedincome.icebofa - Reference | OpenBB SDK Docs" />

Get data for ICE BofA US Corporate Bond Indices.

Source Code: [[link](https://github.com/OpenBB-finance/OpenBBTerminal/tree/main/openbb_terminal/fixedincome/fred_model.py#L793)]

```python wordwrap
openbb.fixedincome.icebofa(data_type: str = "yield", category: str = "all", area: str = "us", grade: str = "non_sovereign", options: bool = False, start_date: Optional[str] = None, end_date: Optional[str] = None)
```

---

## Parameters

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| data_type | str | The type of data you want to see, either "yield", "yield_to_worst", "total_return", or "spread" | yield | True |
| category | str | The type of category you want to see, either "all", "duration", "eur" or "usd". | all | True |
| area | str | The type of area you want to see, either "asia", "emea", "eu", "ex_g10", "latin_america" or "us" | us | True |
| grade | str | The type of grade you want to see, either "a", "aa", "aaa", "b", "bb", "bbb", "ccc", "crossover",<br/>"high_grade", "high_yield", "non_financial", "non_sovereign", "private_sector", "public_sector" | non_sovereign | True |
| options | bool | Set to True to obtain the available options. | False | True |
| start_date | Optional[str] | Start date, formatted YYYY-MM-DD | None | True |
| end_date | Optional[str] | End date, formatted YYYY-MM-DD | None | True |


---

## Returns

This function does not return anything

---

