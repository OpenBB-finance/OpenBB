---
title: rh
description: OpenBB SDK Function
---

# rh

## keys_model.set_rh_key

```python title='openbb_terminal/keys_model.py'
def set_rh_key(username: str, password: str, persist: bool, show_output: bool) -> str:
```
[Source Code](https://github.com/OpenBB-finance/OpenBBTerminal/tree/main/openbb_terminal/keys_model.py#L1108)

Description: Set Robinhood key

## Parameters

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| username | str | User username | None | False |
| password | str | User password | None | False |
| persist | bool | If False, api key change will be contained to where it was changed. For example, Jupyter notebook.
If True, api key change will be global, i.e. it will affect terminal environment variables.
By default, False. | None | False |
| show_output | bool | Display status string or not. By default, False. | None | False |

## Returns

| Type | Description |
| ---- | ----------- |
| str | None |

## Examples

