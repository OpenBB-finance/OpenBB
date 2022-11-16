---
title: messages
description: OpenBB SDK Function
---

import Tabs from '@theme/Tabs';
import TabItem from '@theme/TabItem';

# messages

<Tabs>
<TabItem value="model" label="Model" default>

## stocks_ba_stocktwits_model.get_messages

```python title='openbb_terminal/common/behavioural_analysis/stocktwits_model.py'
def get_messages(symbol: str, limit: int) -> DataFrame:
```
[Source Code](https://github.com/OpenBB-finance/OpenBBTerminal/tree/main/openbb_terminal/common/behavioural_analysis/stocktwits_model.py#L55)

Description: Get last messages for a given ticker [Source: stocktwits]

## Parameters

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| symbol | str | Stock ticker symbol | None | False |
| limit | int | Number of messages to get | None | False |

## Returns

| Type | Description |
| ---- | ----------- |
| pd.DataFrame | Dataframe of messages |

## Examples



</TabItem>
<TabItem value="view" label="View">

## stocks_ba_stocktwits_view.display_messages

```python title='openbb_terminal/common/behavioural_analysis/stocktwits_view.py'
def display_messages(symbol: str, limit: int) -> None:
```
[Source Code](https://github.com/OpenBB-finance/OpenBBTerminal/tree/main/openbb_terminal/common/behavioural_analysis/stocktwits_view.py#L37)

Description: Print up to 30 of the last messages on the board. [Source: Stocktwits]

## Parameters

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| symbol | str | Stock ticker symbol | None | False |
| limit | int | Number of messages to get | None | False |

## Returns

This function does not return anything

## Examples



</TabItem>
</Tabs>