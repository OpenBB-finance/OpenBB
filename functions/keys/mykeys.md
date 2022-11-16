---
title: mykeys
description: OpenBB SDK Function
---

# mykeys

## keys_model.get_keys

```python title='openbb_terminal/keys_model.py'
def get_keys(show: bool) -> DataFrame:
```
[Source Code](https://github.com/OpenBB-finance/OpenBBTerminal/tree/main/openbb_terminal/keys_model.py#L231)

Description: Get currently set API keys.

## Parameters

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| show | bool | Flag to choose whether to show actual keys or not.
By default, False. | None | False |

## Returns

| Type | Description |
| ---- | ----------- |
| pd.DataFrame | Currents keys |

## Examples

