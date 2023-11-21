---
title: tmc
description: Get data for 10-Year Treasury Constant Maturity Minus Selected Treasury Constant Maturity
keywords:
- fixedincome
- tmc
---

import HeadTitle from '@site/src/components/General/HeadTitle.tsx';

<HeadTitle title="fixedincome.tmc - Reference | OpenBB SDK Docs" />

Get data for 10-Year Treasury Constant Maturity Minus Selected Treasury Constant Maturity.

Source Code: [[link](https://github.com/OpenBB-finance/OpenBBTerminal/tree/main/openbb_terminal/fixedincome/fred_model.py#L1124)]

```python wordwrap
openbb.fixedincome.tmc(parameter: str = "3_month", start_date: Optional[str] = None, end_date: Optional[str] = None)
```

---

## Parameters

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| parameter | str | FRED ID of TMC data to plot, options: ["T10Y3M", "T10Y3M"] | 3_month | True |
| start_date | Optional[str] | Start date, formatted YYYY-MM-DD | None | True |
| end_date | Optional[str] | End date, formatted YYYY-MM-DD | None | True |


---

## Returns

This function does not return anything

---

