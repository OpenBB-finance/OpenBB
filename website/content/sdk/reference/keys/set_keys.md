---
title: set_keys
description: Guide on how to set API keys in bundle with OpenBB finance terminal,
  including parameters, return values and examples. Contains source code link
keywords:
- OpenBB terminal
- API keys
- Set keys
- Python code
- Source code
- Jupyter notebook
- Finance
- Environment variables
- Programming guide
---

import HeadTitle from '@site/src/components/General/HeadTitle.tsx';

<HeadTitle title="keys.set_keys - Reference | OpenBB SDK Docs" />

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
