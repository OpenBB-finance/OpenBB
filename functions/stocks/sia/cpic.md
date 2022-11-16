---
title: cpic
description: OpenBB SDK Function
---

import Tabs from '@theme/Tabs';
import TabItem from '@theme/TabItem';

# cpic

<Tabs>
<TabItem value="model" label="Model" default>

## stocks_sia_financedatabase_model.get_companies_per_industry_in_country

```python title='openbb_terminal/stocks/sector_industry_analysis/financedatabase_model.py'
def get_companies_per_industry_in_country(country: str, mktcap: str, exclude_exchanges: bool) -> None:
```
[Source Code](https://github.com/OpenBB-finance/OpenBBTerminal/tree/main/openbb_terminal/stocks/sector_industry_analysis/financedatabase_model.py#L255)

Description: Get number of companies per industry in a specific country (and specific market cap).

## Parameters

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| country | str | Select country to get number of companies by each industry | None | False |
| mktcap | str | Select market cap of companies to consider from Small, Mid and Large | None | False |
| exclude_exchanges | bool | Exclude international exchanges | None | False |

## Returns

| Type | Description |
| ---- | ----------- |
| dict | Dictionary of industries and number of companies in a specific country |

## Examples



</TabItem>
<TabItem value="view" label="View">

## stocks_sia_financedatabase_view.display_companies_per_industry_in_country

```python title='openbb_terminal/stocks/sector_industry_analysis/financedatabase_view.py'
def display_companies_per_industry_in_country(country: str, mktcap: str, exclude_exchanges: bool, export: str, raw: bool, max_industries_to_display: int, min_pct_to_display_industry: float, external_axes: Optional[List[matplotlib.axes._axes.Axes]]) -> None:
```
[Source Code](https://github.com/OpenBB-finance/OpenBBTerminal/tree/main/openbb_terminal/stocks/sector_industry_analysis/financedatabase_view.py#L376)

Description: Display number of companies per industry in a specific country. [Source: Finance Database]

## Parameters

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| country | str | Select country to get number of companies by each industry | None | False |
| mktcap | str | Select market cap of companies to consider from Small, Mid and Large | None | False |
| exclude_exchanges | bool | Exclude international exchanges | None | False |
| export | str | Format to export data as | None | False |
| raw | bool | Output all raw data | None | False |
| max_industries_to_display | int | Maximum number of industries to display | None | False |
| min_pct_to_display_industry | float | Minimum percentage to display industry | None | False |
| external_axes | Optional[List[plt.Axes]] | External axes (1 axis is expected in the list), by default None | None | True |

## Returns

This function does not return anything

## Examples



</TabItem>
</Tabs>