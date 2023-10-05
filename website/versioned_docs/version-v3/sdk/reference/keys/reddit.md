---
title: reddit
description: OpenBB SDK Function
---

# reddit

Set Reddit key

Source Code: [[link](https://github.com/OpenBB-finance/OpenBBTerminal/tree/main/openbb_terminal/keys_model.py#L942)]

```python
openbb.keys.reddit(client_id: str, client_secret: str, password: str, username: str, useragent: str, persist: bool = False, show_output: bool = False)
```

---

## Parameters

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| client_id | str | Client ID | None | False |
| client_secret | str | Client secret | None | False |
| password | str | User password | None | False |
| username | str | User username | None | False |
| useragent | str | User useragent | None | False |
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
openbb.keys.reddit(
```

```
client_id="example_id",
        client_secret="example_secret",
        password="example_password",
        username="example_username",
        useragent="example_useragent"
    )
```
---

