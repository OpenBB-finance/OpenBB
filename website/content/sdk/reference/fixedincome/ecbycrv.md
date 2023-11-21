---
title: ecbycrv
description: Gets euro area yield curve data from ECB
keywords:
- fixedincome
- ecbycrv
---

import HeadTitle from '@site/src/components/General/HeadTitle.tsx';

<HeadTitle title="fixedincome.ecbycrv - Reference | OpenBB SDK Docs" />

Gets euro area yield curve data from ECB.

Source Code: [[link](https://github.com/OpenBB-finance/OpenBBTerminal/tree/main/openbb_terminal/fixedincome/ecb_model.py#L66)]

```python wordwrap
openbb.fixedincome.ecbycrv(date: str = "", yield_type: str = "spot_rate", return_date: bool = False, detailed: bool = False, any_rating: bool = True)
```

---

## Parameters

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| date | str | Date to get curve for. If empty, gets most recent date (format yyyy-mm-dd) |  | True |
| yield_type | str | What type of yield curve to get, options: ['spot_rate', 'instantaneous_forward', 'par_yield'] | spot_rate | True |
| return_date | bool | If True, returns date of yield curve | False | True |
| detailed | bool | If True, returns detailed data. Note that this is very slow. | False | True |
| aaa_only | bool | If True, it only returns rates for AAA rated bonds. If False, it returns rates for all bonds | None | True |


---

## Returns

| Type | Description |
| ---- | ----------- |
| Tuple[pd.DataFrame, str] | Dataframe of yields and maturities,<br/>Date for which the yield curve is obtained |
---

## Examples

```python
from openbb_terminal.sdk import openbb
ycrv_df = openbb.fixedincome.ycrv()
```

```
Since there is a delay with the data, the most recent date is returned and can be accessed with return_date=True
```
```python
ycrv_df, ycrv_date = openbb.fixedincome.ycrv(return_date=True)
```

---

