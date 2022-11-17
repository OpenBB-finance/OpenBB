---
title: oanda
description: OpenBB SDK Function
---

# oanda

## keys_model.set_oanda_key

```python title='openbb_terminal/keys_model.py'
def set_oanda_key(account: str, access_token: str, account_type: str, persist: bool, show_output: bool) -> str:
```
[Source Code](https://github.com/OpenBB-finance/OpenBBTerminal/tree/main/openbb_terminal/keys_model.py#L1248)

Description: Set Oanda key

## Parameters

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| account | str | User account | None | False |
| access_token | str | User token | None | False |
| account_type | str | User account type | None | False |
| persist | bool | If False, api key change will be contained to where it was changed. For example, Jupyter notebook.
If True, api key change will be global, i.e. it will affect terminal environment variables.
By default, False. | None | False |
| show_output | bool | Display status string or not. By default, False. | None | False |

## Returns

| Type | Description |
| ---- | ----------- |
| str | None |

## Examples

