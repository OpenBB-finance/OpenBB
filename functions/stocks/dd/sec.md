---
title: sec
description: OpenBB SDK Function
---

import Tabs from '@theme/Tabs';
import TabItem from '@theme/TabItem';

# sec

<Tabs>
<TabItem value="model" label="Model" default>

## stocks_dd_marketwatch_model.get_sec_filings

```python title='openbb_terminal/stocks/due_diligence/marketwatch_model.py'
def get_sec_filings(symbol: str) -> DataFrame:
```
[Source Code](https://github.com/OpenBB-finance/OpenBBTerminal/tree/main/openbb_terminal/stocks/due_diligence/marketwatch_model.py#L20)

Description: Get SEC filings for a given stock ticker. [Source: Market Watch]

## Parameters

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| symbol | str | Stock ticker symbol | None | False |

## Returns

| Type | Description |
| ---- | ----------- |
| pd.DataFrame | SEC filings data |

## Examples



</TabItem>
<TabItem value="view" label="View">

## stocks_dd_marketwatch_view.sec_filings

```python title='openbb_terminal/stocks/due_diligence/marketwatch_view.py'
def sec_filings(symbol: str, limit: int, export: str) -> None:
```
[Source Code](https://github.com/OpenBB-finance/OpenBBTerminal/tree/main/openbb_terminal/stocks/due_diligence/marketwatch_view.py#L15)

Description: Display SEC filings for a given stock ticker. [Source: Market Watch]

## Parameters

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| symbol | str | Stock ticker symbol | None | False |
| limit | int | Number of ratings to display | None | False |
| export | str | Export dataframe data to csv,json,xlsx file | None | False |

## Returns

This function does not return anything

## Examples



</TabItem>
</Tabs>