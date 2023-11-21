---
title: tbffr
description: Get data for Selected Treasury Bill Minus Federal Funds Rate
keywords:
- fixedincome
- tbffr
---

import HeadTitle from '@site/src/components/General/HeadTitle.tsx';

<HeadTitle title="fixedincome.tbffr - Reference | OpenBB SDK Docs" />

Get data for Selected Treasury Bill Minus Federal Funds Rate.

Source Code: [[link](https://github.com/OpenBB-finance/OpenBBTerminal/tree/main/openbb_terminal/fixedincome/fred_model.py#L1044)]

```python wordwrap
openbb.fixedincome.tbffr(parameter: str = "3_month", start_date: Optional[str] = None, end_date: Optional[str] = None)
```

---

## Parameters

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| parameter | str | FRED ID of TBFFR data to plot, options: ["3_month", "6_month"] | 3_month | True |
| start_date | Optional[str] | Start date, formatted YYYY-MM-DD | None | True |
| end_date | Optional[str] | End date, formatted YYYY-MM-DD | None | True |


---

## Returns

This function does not return anything

---

