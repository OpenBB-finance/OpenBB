---
title: calendar
description: OpenBB SDK Function
---

import Tabs from '@theme/Tabs';
import TabItem from '@theme/TabItem';

# calendar

<Tabs>
<TabItem value="model" label="Model" default>

## forex_oanda_model.get_calendar_request

```python title='openbb_terminal/forex/oanda/oanda_model.py'
def get_calendar_request(days: int, instrument: Optional[str]) -> None:
```
[Source Code](https://github.com/OpenBB-finance/OpenBBTerminal/tree/main/openbb_terminal/forex/oanda/oanda_model.py#L645)

Description: Request data of significant events calendar.

## Parameters

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| instrument | Union[str, None] | The loaded currency pair, by default None | None | False |
| days | int | Number of days in advance | None | False |

## Returns

| Type | Description |
| ---- | ----------- |
| Union[pd.DataFrame, bool] | Calendar events data or False |

## Examples



</TabItem>
<TabItem value="view" label="View">

## forex_oanda_view.calendar

```python title='openbb_terminal/decorators.py'
def calendar() -> None:
```
[Source Code](https://github.com/OpenBB-finance/OpenBBTerminal/tree/main/openbb_terminal/decorators.py#L393)

Description: View calendar of significant events.

## Parameters

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| instrument | str | The loaded currency pair | None | False |
| days | int | Number of days in advance | None | False |

## Returns

This function does not return anything

## Examples



</TabItem>
</Tabs>