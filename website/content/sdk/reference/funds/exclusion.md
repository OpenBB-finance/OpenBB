---
title: exclusion
description: Search mstarpy exclusion policy in esgData
keywords:
- funds
- exclusion
---

import HeadTitle from '@site/src/components/General/HeadTitle.tsx';

<HeadTitle title="funds.exclusion - Reference | OpenBB SDK Docs" />

Search mstarpy exclusion policy in esgData

Source Code: [[link](https://github.com/OpenBB-finance/OpenBBTerminal/tree/main/openbb_terminal/mutual_funds/mstarpy_model.py#L126)]

```python wordwrap
openbb.funds.exclusion(loaded_funds: mstarpy.funds.Funds)
```

---

## Parameters

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| loaded_funds | mstarpy.Funds | class mstarpy.Funds instantiated with selected funds | None | False |


---

## Returns

| Type | Description |
| ---- | ----------- |
| pd.DataFrame | Dataframe containing exclusion policy |
---

## Examples

```python
from openbb_terminal.sdk import openbb
f = openbb.funds.load("Vanguard", "US")
openbb.funds.exclusion(f)
```

---

