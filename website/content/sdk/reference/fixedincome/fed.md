---
title: fed
description: Obtain data for Effective Federal Funds Rate
keywords:
- fixedincome
- fed
---

import HeadTitle from '@site/src/components/General/HeadTitle.tsx';

<HeadTitle title="fixedincome.fed - Reference | OpenBB SDK Docs" />

Obtain data for Effective Federal Funds Rate.

Source Code: [[link](https://github.com/OpenBB-finance/OpenBBTerminal/tree/main/openbb_terminal/fixedincome/fred_model.py#L548)]

```python wordwrap
openbb.fixedincome.fed(parameter: str = "monthly", start_date: Optional[str] = None, end_date: Optional[str] = None, overnight: bool = False, quantiles: bool = False, target: bool = False)
```

---

## Parameters

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| parameter | str | The parameter to get data for. Choose from:<br/>    "monthly"<br/>    "daily"<br/>    "weekly"<br/>    "daily_excl_weekend"<br/>    "annual"<br/>    "biweekly"<br/>    "volume" | monthly | True |
| start_date | Optional[str] | Start date, formatted YYYY-MM-DD | None | True |
| end_date | Optional[str] | End date, formatted YYYY-MM-DD | None | True |
| overnight | bool | Whether you want to plot the Overnight Banking Federal Rate | False | True |
| quantiles | bool | Whether you want to see the 1, 25, 75 and 99 percentiles | False | True |
| target | bool | Whether you want to see the high and low target range | False | True |


---

## Returns

This function does not return anything

---

