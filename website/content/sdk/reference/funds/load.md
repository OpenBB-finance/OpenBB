---
title: load
description: Search mstarpy for matching funds
keywords:
- funds
- load
---

import HeadTitle from '@site/src/components/General/HeadTitle.tsx';

<HeadTitle title="funds.load - Reference | OpenBB SDK Docs" />

Search mstarpy for matching funds

Source Code: [[link](https://github.com/OpenBB-finance/OpenBBTerminal/tree/main/openbb_terminal/mutual_funds/mstarpy_model.py#L154)]

```python wordwrap
openbb.funds.load(term: str = "", country: str = "US")
```

---

## Parameters

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| term | str | String that will be searched for.  Can be name or isin |  | True |
| country | str | country where the funds is hosted | US | True |


---

## Returns

| Type | Description |
| ---- | ----------- |
| mstarpy.Funds | class mstarpy.Funds instantiated with selected funds |
---

## Examples

```python
from openbb_terminal.sdk import openbb
f = openbb.funds.load("Vanguard", "US")
```

---

