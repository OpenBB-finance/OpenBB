---
title: binance
description: OpenBB SDK Function
---

# binance

## keys_model.set_binance_key

```python title='openbb_terminal/keys_model.py'
def set_binance_key(key: str, secret: str, persist: bool, show_output: bool) -> str:
```
[Source Code](https://github.com/OpenBB-finance/OpenBBTerminal/tree/main/openbb_terminal/keys_model.py#L1323)

Description: Set Binance key

## Parameters

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| key | str | API key | None | False |
| secret | str | API secret | None | False |
| persist | bool | If False, api key change will be contained to where it was changed. For example, Jupyter notebook.
If True, api key change will be global, i.e. it will affect terminal environment variables.
By default, False. | None | False |
| show_output | bool | Display status string or not. By default, False. | None | False |

## Returns

| Type | Description |
| ---- | ----------- |
| str | None |

## Examples

