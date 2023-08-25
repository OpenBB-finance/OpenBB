---
title: degiro
description: OpenBB SDK Function
---

# degiro

Set Degiro key

Source Code: [[link](https://github.com/OpenBB-finance/OpenBBTerminal/tree/main/openbb_terminal/keys_model.py#L1296)]

```python
openbb.keys.degiro(username: str, password: str, secret: str = "", persist: bool = False, show_output: bool = False)
```

---

## Parameters

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| username | str | User username | None | False |
| password | str | User password | None | False |
| secret | str | User secret |  | True |
| persist | bool | If False, api key change will be contained to where it was changed. For example, a Jupyter notebook session.<br/>If True, api key change will be global, i.e. it will affect terminal environment variables.<br/>By default, False. | False | True |
| show_output | bool | Display status string or not. By default, False. | False | True |


---

## Returns

| Type | Description |
| ---- | ----------- |
| str | Status of key set |
---

## Examples

```python
from openbb_terminal.sdk import openbb
openbb.keys.degiro(
```

```
username="example_username",
        password="example_password"
    )
```
---

