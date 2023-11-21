---
title: sofr
description: Obtain data for Secured Overnight Financing Rate (SOFR)
keywords:
- fixedincome
- sofr
---

import HeadTitle from '@site/src/components/General/HeadTitle.tsx';

<HeadTitle title="fixedincome.sofr - Reference | OpenBB SDK Docs" />

Obtain data for Secured Overnight Financing Rate (SOFR)

Source Code: [[link](https://github.com/OpenBB-finance/OpenBBTerminal/tree/main/openbb_terminal/fixedincome/fred_model.py#L456)]

```python wordwrap
openbb.fixedincome.sofr(parameter: str = "overnight", start_date: Optional[str] = None, end_date: Optional[str] = None)
```

---

## Parameters

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| parameter | str | The parameter to get data for. Choose from:<br/>    "overnight"<br/>    "30_day_average"<br/>    "90_day_average"<br/>    "180_day_average"<br/>    "index" | overnight | True |
| start_date | Optional[str] | Start date, formatted YYYY-MM-DD | None | True |
| end_date | Optional[str] | End date, formatted YYYY-MM-DD | None | True |


---

## Returns

This function does not return anything

---

