---
title: future
description: This page provides detailed documentation on how to use OpenBB's 'future'
  function in Python script. It explains parameters and returns related to different
  financial instruments.
keywords:
- OpenBB future function
- Python script
- financial instruments
- Indices
- Energy
- Metals
- Meats
- Grains
- Softs
- Bonds
- Currencies
- Finviz
---

import HeadTitle from '@site/src/components/General/HeadTitle.tsx';

<HeadTitle title="economy.future - Reference | OpenBB SDK Docs" />

Get futures data. [Source: Finviz]

Source Code: [[link](https://github.com/OpenBB-finance/OpenBBTerminal/tree/main/openbb_terminal/economy/finviz_model.py#L187)]

```python
openbb.economy.future(future_type: str = "Indices", sortby: str = "ticker", ascend: bool = False)
```

---

## Parameters

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| future_type | str | From the following: Indices, Energy, Metals, Meats, Grains, Softs, Bonds, Currencies | Indices | True |
| sortby | str | Column to sort by | ticker | True |
| ascend | bool | Flag to sort in ascending order | False | True |


---

## Returns

| Type | Description |
| ---- | ----------- |
| pd.Dataframe | Indices, Energy, Metals, Meats, Grains, Softs, Bonds, Currencies |
---
