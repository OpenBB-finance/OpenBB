---
title: rh
description: This page provides detailed information on setting the Robinhood key
  using the openbb keys function. It includes source code, parameters description,
  return types, and usage examples. This Python SDK function allows users to handle
  their Robinhood key in different environments including Jupyter notebook sessions
  and terminal environment variables.
keywords:
- Robinhood
- keys
- username and password
- API key
- Jupyter notebook session
- terminal environment variables
---

import HeadTitle from '@site/src/components/General/HeadTitle.tsx';

<HeadTitle title="keys.rh - Reference | OpenBB SDK Docs" />

Set Robinhood key

Source Code: [[link](https://github.com/OpenBB-finance/OpenBBTerminal/tree/main/openbb_terminal/keys_model.py#L1227)]

```python
openbb.keys.rh(username: str, password: str, persist: bool = False, show_output: bool = False)
```

---

## Parameters

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| username | str | User username | None | False |
| password | str | User password | None | False |
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
openbb.keys.rh(
```

```
username="example_username",
        password="example_password"
    )
```
---
