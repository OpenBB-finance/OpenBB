---
title: mykeys
description: OpenBB SDK Function
---

# mykeys

Get currently set API keys.

Source Code: [[link](https://github.com/OpenBB-finance/OpenBBTerminal/tree/main/openbb_terminal/keys_model.py#L241)]

```python
openbb.keys.mykeys(show: bool = False)
```

---

## Parameters

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| show | bool | Flag to choose whether to show actual keys or not.<br/>By default, False. | False | True |


---

## Returns

| Type | Description |
| ---- | ----------- |
| pd.DataFrame | Currents keys |
---

## Examples

```python
from openbb_terminal.sdk import openbb
openbb.keys.mykeys()
```

```
Key
          API
 BITQUERY_KEY  *******
      CMC_KEY  *******
COINGLASS_KEY  *******
```
---

