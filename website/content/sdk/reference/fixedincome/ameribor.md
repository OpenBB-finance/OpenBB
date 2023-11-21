---
title: ameribor
description: Obtain data for American Interbank Offered Rate (AMERIBOR)
keywords:
- fixedincome
- ameribor
---

import HeadTitle from '@site/src/components/General/HeadTitle.tsx';

<HeadTitle title="fixedincome.ameribor - Reference | OpenBB SDK Docs" />

Obtain data for American Interbank Offered Rate (AMERIBOR)

Source Code: [[link](https://github.com/OpenBB-finance/OpenBBTerminal/tree/main/openbb_terminal/fixedincome/fred_model.py#L513)]

```python wordwrap
openbb.fixedincome.ameribor(parameter: str = "overnight", start_date: Optional[str] = None, end_date: Optional[str] = None)
```

---

## Parameters

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| parameter | str | The parameter to get data for. Choose from:<br/>    "overnight": "AMERIBOR",<br/>    "term_30": "AMBOR30T",<br/>    "term_90": "AMBOR90T",<br/>    "1_week_term_structure": "AMBOR1W",<br/>    "1_month_term_structure": "AMBOR1M",<br/>    "3_month_term_structure": "AMBOR3M",<br/>    "6_month_term_structure": "AMBOR6M",<br/>    "1_year_term_structure": "AMBOR1Y",<br/>    "2_year_term_structure": "AMBOR2Y",<br/>    "30_day_ma": "AMBOR30",<br/>    "90_day_ma": "AMBOR90", | overnight | True |
| start_date | Optional[str] | Start date, formatted YYYY-MM-DD | None | True |
| end_date | Optional[str] | End date, formatted YYYY-MM-DD | None | True |


---

## Returns

This function does not return anything

---

