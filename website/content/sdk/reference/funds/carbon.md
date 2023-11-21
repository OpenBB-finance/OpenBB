---
title: carbon
description: Search mstarpy for carbon metrics
keywords:
- funds
- carbon
---

import HeadTitle from '@site/src/components/General/HeadTitle.tsx';

<HeadTitle title="funds.carbon - Reference | OpenBB SDK Docs" />

Search mstarpy for carbon metrics

Source Code: [[link](https://github.com/OpenBB-finance/OpenBBTerminal/tree/main/openbb_terminal/mutual_funds/mstarpy_model.py#L102)]

```python wordwrap
openbb.funds.carbon(loaded_funds: mstarpy.funds.Funds)
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
| pd.DataFrame | Dataframe containing carbon metrics |
---

## Examples

```python
from openbb_terminal.sdk import openbb
f = openbb.funds.load("Vanguard", "US")
openbb.funds.carbon(f)
```

---

