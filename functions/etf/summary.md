---
title: summary
description: OpenBB SDK Function
---

import Tabs from '@theme/Tabs';
import TabItem from '@theme/TabItem';

# summary

<Tabs>
<TabItem value="model" label="Model" default>

## etf_yfinance_model.get_etf_summary_description

```python title='openbb_terminal/etf/yfinance_model.py'
def get_etf_summary_description(name: str) -> str:
```
[Source Code](https://github.com/OpenBB-finance/OpenBBTerminal/tree/main/openbb_terminal/etf/yfinance_model.py#L44)

Description: Return summary description of ETF. [Source: Yahoo Finance]

## Parameters

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| name | str | ETF name | None | False |
| Returns | None | None | None | None |
| ---------- | None | None | None | None |
| str | None | Summary description of the ETF | None | None |

## Returns

This function does not return anything

## Examples



</TabItem>
<TabItem value="view" label="View">

## etf_yfinance_view.display_etf_description

```python title='openbb_terminal/etf/yfinance_view.py'
def display_etf_description(name: str) -> None:
```
[Source Code](https://github.com/OpenBB-finance/OpenBBTerminal/tree/main/openbb_terminal/etf/yfinance_view.py#L103)

Description: Display ETF description summary. [Source: Yahoo Finance]

## Parameters

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| name | str | ETF name | None | False |

## Returns

This function does not return anything

## Examples



</TabItem>
</Tabs>