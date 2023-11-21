---
title: dwpcr
description: Obtain data for the Discount Window Primary Credit Rate
keywords:
- fixedincome
- dwpcr
---

import HeadTitle from '@site/src/components/General/HeadTitle.tsx';

<HeadTitle title="fixedincome.dwpcr - Reference | OpenBB SDK Docs" />

Obtain data for the Discount Window Primary Credit Rate.

Source Code: [[link](https://github.com/OpenBB-finance/OpenBBTerminal/tree/main/openbb_terminal/fixedincome/fred_model.py#L660)]

```python wordwrap
openbb.fixedincome.dwpcr(parameter: str = "daily_excl_weekend", start_date: Optional[str] = None, end_date: Optional[str] = None)
```

---

## Parameters

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| parameter | str | The parameter to get data for. Choose from:<br/>    "daily_excl_weekend"<br/>    "monthly"<br/>    "weekly"<br/>    "daily"<br/>    "annual" | daily_excl_weekend | True |
| start_date | Optional[str] | Start date, formatted YYYY-MM-DD | None | True |
| end_date | Optional[str] | End date, formatted YYYY-MM-DD | None | True |


---

## Returns

This function does not return anything

---

