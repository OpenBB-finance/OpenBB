---
title: usrates
description: Plot various treasury rates from the United States
keywords:
- fixedincome
- usrates
---

import HeadTitle from '@site/src/components/General/HeadTitle.tsx';

<HeadTitle title="fixedincome.usrates - Reference | OpenBB SDK Docs" />

Plot various treasury rates from the United States

Source Code: [[link](https://github.com/OpenBB-finance/OpenBBTerminal/tree/main/openbb_terminal/fixedincome/fred_model.py#L739)]

```python wordwrap
openbb.fixedincome.usrates(parameter: str = "tbills", maturity: str = "3_months", start_date: Optional[str] = None, end_date: Optional[str] = None)
```

---

## Parameters

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| parameter | str | Either "tbills", "cmn", or "tips". | tbills | True |
| maturity | str | Depending on the chosen parameter, a set of maturities is available.<br/>    "4_week": {"tbill": "DTB4WK"},<br/>    "1_month": {"cmn": "DGS1MO"},<br/>    "3_month": {"tbill": "TB3MS", "cmn": "DGS3MO"},<br/>    "6_month": {"tbill": "DTB6", "cmn": "DGS6MO"},<br/>    "1_year": {"tbill": "DTB1YR", "cmn": "DGS1"},<br/>    "2_year": {"cmn": "DGS2"},<br/>    "3_year": {"cmn": "DGS3"},<br/>    "5_year": {"tips": "DFII5", "cmn": "DGS5"},<br/>    "7_year": {"tips": "DFII7", "cmn": "DGS7"},<br/>    "10_year": {"tips": "DFII10", "cmn": "DGS10"},<br/>    "20_year": {"tips": "DFII20", "cmn": "DGS20"},<br/>    "30_year": {"tips": "DFII30", "cmn": "DGS30"}, | 3_months | True |
| start_date | Optional[str] | Start date, formatted YYYY-MM-DD | None | True |
| end_date | Optional[str] | End date, formatted YYYY-MM-DD | None | True |


---

## Returns

This function does not return anything

---

