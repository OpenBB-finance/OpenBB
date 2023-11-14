---
title: load
description: Documentation for the 'load' function from the OpenBB forecast library.
  This function permits to load a custom file into a DataFrame within Python. It covers
  instructions, source code, parameters, and returns.
keywords:
- load
- custom file
- dataframe
- forecast
- parameters
- data_files
- data_examples
---

import HeadTitle from '@site/src/components/General/HeadTitle.tsx';

<HeadTitle title="forecast.load - Reference | OpenBB SDK Docs" />

Load custom file into dataframe.

Source Code: [[link](https://github.com/OpenBB-finance/OpenBBTerminal/tree/main/openbb_terminal/common/common_model.py#L53)]

```python
openbb.forecast.load(file: str, data_files: Optional[Dict[Any, Any]] = None, data_examples: Optional[Dict[Any, Any]] = None)
```

---

## Parameters

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| file | str | Path to file | None | False |
| data_files | dict | Contains all available data files within the Export folder | None | True |
| data_examples | dict | Contains all available examples from Statsmodels | None | True |


---

## Returns

| Type | Description |
| ---- | ----------- |
| pd.DataFrame | Dataframe with custom data |
---
