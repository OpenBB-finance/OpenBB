---
title: rvol_std
description: Standard deviation measures how widely returns are dispersed from the average return
keywords:
- ta
- rvol_std
---

import HeadTitle from '@site/src/components/General/HeadTitle.tsx';

<HeadTitle title="ta.rvol_std - Reference | OpenBB SDK Docs" />

Standard deviation measures how widely returns are dispersed from the average return.

Source Code: [[link](https://github.com/OpenBB-finance/OpenBBTerminal/tree/main/openbb_terminal/common/technical_analysis/volatility_model.py#L185)]

```python wordwrap
openbb.ta.rvol_std(data: pd.DataFrame, window: int = 30, trading_periods: Optional[int] = None, is_crypto: bool = False, clean: bool = True)
```

---

## Parameters

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| data | pd.DataFrame | Dataframe of OHLC prices. | None | False |
| window | int [default: 30] | Length of window to calculate over. | 30 | True |
| trading_periods | Optional[int] [default: 252] | Number of trading periods in a year. | None | True |
| is_crypto | bool [default: False] | If true, trading_periods is defined as 365. | False | True |
| clean | bool [default: True] | Whether to clean the data or not by dropping NaN values. | True | True |


---

## Returns

| Type | Description |
| ---- | ----------- |
| results | Dataframe with results. |
---

## Examples

```python
data = openbb.stocks.load('SPY')
df = openbb.ta.standard_deviation(data)
```

---

