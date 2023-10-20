---
title: set_keys
description: OpenBB SDK Function
---

# set_keys

Set API keys in bundle.

Source Code: [[link](https://github.com/OpenBB-finance/OpenBBTerminal/tree/main/openbb_terminal/keys_model.py#L116)]

```python
openbb.keys.set_keys(keys_dict: Dict[str, Dict[str, Union[str, bool]]], persist: bool = False, show_output: bool = False)
```

---

## Parameters

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| keys_dict | Dict[str, Dict[str, Union[str, bool]]] | More info on the required inputs for each API can be found on `keys.get_keys_info()` | None | False |
| persist | bool | If False, api key change will be contained to where it was changed. For example, a Jupyter notebook session.<br/>If True, api key change will be global, i.e. it will affect terminal environment variables.<br/>By default, False. | False | True |
| show_output | bool | Display status string or not. By default, False. | False | True |


---

## Returns

| Type | Description |
| ---- | ----------- |
| Dict | Status of each key set. |
---

## Examples

```python
from openbb_terminal.sdk import openbb
d = {
```

```
"fred": {"key": "XXXXX"},
        "binance": {"key": "YYYYY", "secret": "ZZZZZ"},
    }
```
```python
openbb.keys.set_keys(keys_dict=d)
```

---

