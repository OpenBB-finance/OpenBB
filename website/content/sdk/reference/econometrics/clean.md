---
title: clean
description: This documentation details how to use OpenBBTerminal's 'clean' function
  to clean up NaNs in a pandas DataFrame. It outlines the parameters, return values,
  and available methods for filling and dropping NaN values.
keywords:
- econometrics
- clean data
- NaN handling
- machine learning
- dataset cleaning
- fill method
- drop method
- data pre-processing
---

import HeadTitle from '@site/src/components/General/HeadTitle.tsx';

<HeadTitle title="econometrics.clean - Reference | OpenBB SDK Docs" />

Clean up NaNs from the dataset

Source Code: [[link](https://github.com/OpenBB-finance/OpenBBTerminal/tree/main/openbb_terminal/econometrics/econometrics_model.py#L65)]

```python
openbb.econometrics.clean(dataset: pd.DataFrame, fill: str = "", drop: str = "", limit: Optional[int] = None)
```

---

## Parameters

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| dataset | pd.DataFrame | The dataset you wish to clean | None | False |
| fill | str | The method of filling NaNs. Choose from:<br/>rfill, cfill, rbfill, cbfill, rffill, cffill |  | True |
| drop | str | The method of dropping NaNs. Choose from:<br/>rdrop, cdrop |  | True |
| limit | int | The maximum limit you wish to apply that can be forward or backward filled | None | True |


---

## Returns

| Type | Description |
| ---- | ----------- |
| pd.DataFrame | Dataframe with cleaned up data |
---
