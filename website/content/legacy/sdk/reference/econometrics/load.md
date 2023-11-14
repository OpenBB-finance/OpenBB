---
title: load
description: The page provides information on loading custom files into a dataframe
  in OpenBB. It offers the function definition, parameters, and returns
keywords:
- dataframe
- load function
- custom files
- parameters
- returns
- Statsmodels examples
- Export folder
---

import HeadTitle from '@site/src/components/General/HeadTitle.tsx';

<HeadTitle title="econometrics.load - Reference | OpenBB SDK Docs" />

Load custom file into dataframe.

Source Code: [[link](https://github.com/OpenBB-finance/OpenBBTerminal/tree/main/openbb_terminal/common/common_model.py#L53)]

```python
openbb.econometrics.load(file: str, data_files: Optional[Dict[Any, Any]] = None, data_examples: Optional[Dict[Any, Any]] = None)
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
