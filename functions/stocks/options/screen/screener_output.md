---
title: screener_output
description: OpenBB SDK Function
---

import Tabs from '@theme/Tabs';
import TabItem from '@theme/TabItem';

# screener_output

<Tabs>
<TabItem value="model" label="Model" default>

## stocks_options_screen_syncretism_model.get_screener_output

```python title='openbb_terminal/stocks/options/screen/syncretism_model.py'
def get_screener_output(preset: str) -> None:
```
[Source Code](https://github.com/OpenBB-finance/OpenBBTerminal/tree/main/openbb_terminal/stocks/options/screen/syncretism_model.py#L159)

Description: Screen options based on preset filters

## Parameters

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| preset | str | Chosen preset | None | False |

## Returns

| Type | Description |
| ---- | ----------- |
|  | DataFrame with screener data, or empty if errors |

## Examples



</TabItem>
<TabItem value="view" label="View">

## stocks_options_screen_syncretism_view.view_screener_output

```python title='openbb_terminal/stocks/options/screen/syncretism_view.py'
def view_screener_output(preset: str, limit: int, export: str) -> None:
```
[Source Code](https://github.com/OpenBB-finance/OpenBBTerminal/tree/main/openbb_terminal/stocks/options/screen/syncretism_view.py#L59)

Description: Print the output of screener

## Parameters

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| preset | str | Chosen preset | None | False |
| limit | int | Number of randomly sorted rows to display | None | False |
| export | str | Format for export file | None | False |

## Returns

| Type | Description |
| ---- | ----------- |
| List | List of tickers screened |

## Examples



</TabItem>
</Tabs>