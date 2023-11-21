---
title: vif
description: Calculates VIF (variance inflation factor), which tests collinearity
keywords:
- econometrics
- vif
---

import HeadTitle from '@site/src/components/General/HeadTitle.tsx';

<HeadTitle title="econometrics.vif - Reference | OpenBB SDK Docs" />

Calculates VIF (variance inflation factor), which tests collinearity.

Source Code: [[link](https://github.com/OpenBB-finance/OpenBBTerminal/tree/main/openbb_terminal/econometrics/econometrics_model.py#L489)]

```python wordwrap
openbb.econometrics.vif(dataset: pd.DataFrame, columns: Optional[list] = None)
```

---

## Parameters

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| dataset | pd.Series | Dataset to calculate VIF on | None | False |
| columns | Optional[list] | The columns to calculate to test for collinearity | None | True |


---

## Returns

| Type | Description |
| ---- | ----------- |
| pd.DataFrame | Dataframe with the resulting VIF values for the selected columns |
---

## Examples

```python
from openbb_terminal.sdk import openbb
longley = openbb.econometrics.load("longley")
openbb.econometrics.vif(longley, ["TOTEMP","UNEMP","ARMED"])
```

---

