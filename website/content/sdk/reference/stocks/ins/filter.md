---
title: filter
description: GEt insider trades based on preset filter
keywords:
- stocks
- ins
- filter
---

import HeadTitle from '@site/src/components/General/HeadTitle.tsx';

<HeadTitle title="stocks.ins.filter - Reference | OpenBB SDK Docs" />

GEt insider trades based on preset filter

Source Code: [[link](https://github.com/OpenBB-finance/OpenBBTerminal/tree/main/openbb_terminal/stocks/insider/sdk_helper.py#L31)]

```python wordwrap
openbb.stocks.ins.filter(preset: str)
```

---

## Parameters

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| preset | str | Name of preset filter | None | False |


---

## Returns

| Type | Description |
| ---- | ----------- |
| pd.DataFrame | DataFrame of filtered insider data |
---

## Examples

```python
from openbb_terminal.sdk import openbb
```

```
In order to filter, we pass one of the predefined .ini filters from OpenBBUserData/presets/stocks/insider
```
```python
filter = "Gold-Silver"
insider_trades = openbb.stocks.ins.filter(filter)
```

---

