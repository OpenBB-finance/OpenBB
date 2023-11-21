---
title: moody
description: Get data for Moody Corporate Bond Index
keywords:
- fixedincome
- moody
---

import HeadTitle from '@site/src/components/General/HeadTitle.tsx';

<HeadTitle title="fixedincome.moody - Reference | OpenBB SDK Docs" />

Get data for Moody Corporate Bond Index

Source Code: [[link](https://github.com/OpenBB-finance/OpenBBTerminal/tree/main/openbb_terminal/fixedincome/fred_model.py#L876)]

```python wordwrap
openbb.fixedincome.moody(data_type: str = "aaa", spread: Optional[str] = None, start_date: Optional[str] = None, end_date: Optional[str] = None)
```

---

## Parameters

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| data_type | str | The type of data you want to see, either "aaa" or "baa" | aaa | True |
| spread | Optional[str] | Whether you want to show the spread for treasury or fed_funds | None | True |
| start_date | Optional[str] | Start date, formatted YYYY-MM-DD | None | True |
| end_date | Optional[str] | End date, formatted YYYY-MM-DD | None | True |


---

## Returns

This function does not return anything

---

