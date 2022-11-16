---
title: cps
description: OpenBB SDK Function
---

import Tabs from '@theme/Tabs';
import TabItem from '@theme/TabItem';

# cps

<Tabs>
<TabItem value="model" label="Model" default>

## stocks_sia_financedatabase_model.get_companies_per_sector_in_country

```python title='openbb_terminal/stocks/sector_industry_analysis/financedatabase_model.py'
def get_companies_per_sector_in_country(country: str, mktcap: str, exclude_exchanges: bool) -> dict:
```
[Source Code](https://github.com/OpenBB-finance/OpenBBTerminal/tree/main/openbb_terminal/stocks/sector_industry_analysis/financedatabase_model.py#L205)

Description: Get number of companies per sector in a specific country (and specific market cap). [Source: Finance Database]

## Parameters

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| country | str | Select country to get number of companies by each sector | None | False |
| mktcap | str | Select market cap of companies to consider from Small, Mid and Large | None | False |
| exclude_exchanges | bool | Exclude international exchanges | None | False |

## Returns

| Type | Description |
| ---- | ----------- |
| dict | Dictionary of sectors and number of companies in a specific country |

## Examples



</TabItem>
<TabItem value="view" label="View">

## stocks_sia_financedatabase_view.display_companies_per_sector_in_country

```python title='openbb_terminal/stocks/sector_industry_analysis/financedatabase_view.py'
def display_companies_per_sector_in_country(country: str, mktcap: str, exclude_exchanges: bool, export: str, raw: bool, max_sectors_to_display: int, min_pct_to_display_sector: float, external_axes: Optional[List[matplotlib.axes._axes.Axes]]) -> None:
```
[Source Code](https://github.com/OpenBB-finance/OpenBBTerminal/tree/main/openbb_terminal/stocks/sector_industry_analysis/financedatabase_view.py#L238)

Description: Display number of companies per sector in a specific country (and market cap). [Source: Finance Database]

## Parameters

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| country | str | Select country to get number of companies by each sector | None | False |
| mktcap | str | Select market cap of companies to consider from Small, Mid and Large | None | False |
| exclude_exchanges | bool | Exclude international exchanges | None | False |
| export | str | Format to export data as | None | False |
| raw | bool | Output all raw data | None | False |
| max_sectors_to_display | int | Maximum number of sectors to display | None | False |
| min_pct_to_display_sector | float | Minimum percentage to display sector | None | False |
| external_axes | Optional[List[plt.Axes]] | External axes (1 axis is expected in the list), by default None | None | True |

## Returns

This function does not return anything

## Examples



</TabItem>
</Tabs>