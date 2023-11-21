---
title: treasury
description: Gets interest rates data from selected countries (3 month and 10 year)
keywords:
- fixedincome
- treasury
---

import HeadTitle from '@site/src/components/General/HeadTitle.tsx';

<HeadTitle title="fixedincome.treasury - Reference | OpenBB SDK Docs" />

Gets interest rates data from selected countries (3 month and 10 year)

Source Code: [[link](https://github.com/OpenBB-finance/OpenBBTerminal/tree/main/openbb_terminal/fixedincome/oecd_model.py#L247)]

```python wordwrap
openbb.fixedincome.treasury(short_term: Optional[list] = None, long_term: Optional[list] = None, forecast: bool = False, start_date: Optional[str] = None, end_date: Optional[str] = None)
```

---

## Parameters

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| short_term | list | Countries you wish to plot the 3-month interest rate for | None | True |
| long_term | list | Countries you wish to plot the 10-year interest rate for | None | True |
| forecast | bool | If True, plot forecasts for short term interest rates | False | True |
| start_date | str | Start date of data, in YYYY-MM-DD format | None | True |
| end_date | str | End date of data, in YYYY-MM-DD format | None | True |


---

## Returns

This function does not return anything

---

