---
title: reddit
description: OpenBB SDK Function
---

# reddit

## keys_model.set_reddit_key

```python title='openbb_terminal/keys_model.py'
def set_reddit_key(client_id: str, client_secret: str, password: str, username: str, useragent: str, persist: bool, show_output: bool) -> str:
```
[Source Code](https://github.com/OpenBB-finance/OpenBBTerminal/tree/main/openbb_terminal/keys_model.py#L854)

Description: Set Reddit key

## Parameters

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| client_id | str | Client ID | None | False |
| client_secret | str | Client secret | None | False |
| password | str | User assword | None | False |
| username | str | User username | None | False |
| useragent | str | User useragent | None | False |
| persist | bool | If False, api key change will be contained to where it was changed. For example, Jupyter notebook.
If True, api key change will be global, i.e. it will affect terminal environment variables.
By default, False. | None | False |
| show_output | bool | Display status string or not. By default, False. | None | False |

## Returns

| Type | Description |
| ---- | ----------- |
| str | None |

## Examples

