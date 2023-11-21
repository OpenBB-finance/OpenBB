---
title: cp
description: Obtain Commercial Paper data
keywords:
- fixedincome
- cp
---

import HeadTitle from '@site/src/components/General/HeadTitle.tsx';

<HeadTitle title="fixedincome.cp - Reference | OpenBB SDK Docs" />

Obtain Commercial Paper data

Source Code: [[link](https://github.com/OpenBB-finance/OpenBBTerminal/tree/main/openbb_terminal/fixedincome/fred_model.py#L907)]

```python wordwrap
openbb.fixedincome.cp(maturity: str = "30d", category: str = "financial", grade: str = "aa", start_date: Optional[str] = None, end_date: Optional[str] = None)
```

---

## Parameters

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| maturity | str | The maturity you want to see, either "overnight", "7d", "15d", "30d", "60d" or "90d" | 30d | True |
| category | str | The category you want to see, either "asset_backed", "financial" or "non_financial" | financial | True |
| grade | str | The type of grade you want to see, either "a2_p2" or "aa" | aa | True |
| description | bool | Whether you wish to obtain a description of the data. | None | True |
| start_date | Optional[str] | Start date, formatted YYYY-MM-DD | None | True |
| end_date | Optional[str] | End date, formatted YYYY-MM-DD | None | True |


---

## Returns

This function does not return anything

---

