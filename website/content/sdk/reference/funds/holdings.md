---
title: holdings
description: Search mstarpy for holdings
keywords:
- funds
- holdings
---

import HeadTitle from '@site/src/components/General/HeadTitle.tsx';

<HeadTitle title="funds.holdings - Reference | OpenBB SDK Docs" />

Search mstarpy for holdings

Source Code: [[link](https://github.com/OpenBB-finance/OpenBBTerminal/tree/main/openbb_terminal/mutual_funds/mstarpy_model.py#L181)]

```python wordwrap
openbb.funds.holdings(loaded_funds: mstarpy.funds.Funds, holding_type: str = "all")
```

---

## Parameters

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| loaded_funds | mstarpy.Funds | class mstarpy.Funds instantiated with selected funds | None | False |
| holding_type | str | type of holdings, can be all, equity, bond, other | all | True |


---

## Returns

| Type | Description |
| ---- | ----------- |
| pd.DataFrame | Dataframe containing holdings |
---

## Examples

```python
from openbb_terminal.sdk import openbb
f = openbb.funds.load("Vanguard", "US")
openbb.funds.holdings(f)
```

---

