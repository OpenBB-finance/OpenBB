---
title: spot
description: The spot rate for any maturity is the yield on a bond that provides
keywords:
- fixedincome
- spot
---

import HeadTitle from '@site/src/components/General/HeadTitle.tsx';

<HeadTitle title="fixedincome.spot - Reference | OpenBB SDK Docs" />

The spot rate for any maturity is the yield on a bond that provides

Source Code: [[link](https://github.com/OpenBB-finance/OpenBBTerminal/tree/main/openbb_terminal/fixedincome/fred_model.py#L957)]

```python wordwrap
openbb.fixedincome.spot(maturity: List = ['10y'], category: List = ['spot_rate'], start_date: Optional[str] = None, end_date: Optional[str] = None)
```

---

## Parameters

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| maturity | str | The maturity you want to see (ranging from '1y' to '100y' in interval of 0.5, e.g. '50.5y') | ['10y'] | True |
| category | list | The category you want to see ('par_yield' and/or 'spot_rate') | ['spot_rate'] | True |
| description | bool | Whether you wish to obtain a description of the data. | None | True |
| start_date | Optional[str] | Start date, formatted YYYY-MM-DD | None | True |
| end_date | Optional[str] | End date, formatted YYYY-MM-DD | None | True |


---

## Returns

This function does not return anything

---

