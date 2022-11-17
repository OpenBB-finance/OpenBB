---
title: set_keys
description: OpenBB SDK Function
---

# set_keys

## keys_model.set_keys

```python title='openbb_terminal/keys_model.py'
def set_keys(keys_dict: Dict[str, Dict[str, Union[str, bool]]], persist: bool, show_output: bool) -> None:
```
[Source Code](https://github.com/OpenBB-finance/OpenBBTerminal/tree/main/openbb_terminal/keys_model.py#L116)

Description: Set API keys in bundle.

## Parameters

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| keys_dict | Dict[str, Dict[str, Union[str, bool]]] | E.g. {"fred": {"key":"XXXXX"}, "binance": {"key":"YYYYY", "secret":"ZZZZZ"}}
More info on APIs can be found through get_keys_info(). | None | False |
| persist | bool | If False, api key change will be contained to where it was changed. For example, Jupyter notebook.
If True, api key change will be global, i.e. it will affect terminal environment variables.
By default, False. | None | False |
| show_output | bool | Display status string or not. By default, False. | None | False |

## Returns

| Type | Description |
| ---- | ----------- |
| Dict | None |

## Examples

