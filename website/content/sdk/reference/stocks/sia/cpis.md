---
title: cpis
description: OpenBB SDK Function
---

import Tabs from '@theme/Tabs';
import TabItem from '@theme/TabItem';

# cpis

<Tabs>
<TabItem value="model" label="Model" default>

Get number of companies per industry in a specific sector (and specific market cap).

Source Code: [[link](https://github.com/OpenBB-finance/OpenBBTerminal/tree/main/openbb_terminal/stocks/sector_industry_analysis/financedatabase_model.py#L309)]

```python
openbb.stocks.sia.cpis(sector: str = "Technology", mktcap: str = "Large", exclude_exchanges: bool = True)
```

---

## Parameters

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| sector | str | Select sector to get number of companies by each industry | Technology | True |
| mktcap | str | Select market cap of companies to consider from Small, Mid and Large | Large | True |
| exclude_exchanges | bool | Exclude international exchanges | True | True |


---

## Returns

| Type | Description |
| ---- | ----------- |
| dict | Dictionary of industries and number of companies in a specific sector |
---



</TabItem>
<TabItem value="view" label="Chart">

Display number of companies per industry in a specific sector. [Source: Finance Database]

Source Code: [[link](https://github.com/OpenBB-finance/OpenBBTerminal/tree/main/openbb_terminal/stocks/sector_industry_analysis/financedatabase_view.py#L525)]

```python
openbb.stocks.sia.cpis_chart(sector: str = "Technology", mktcap: str = "Large", exclude_exchanges: bool = True, export: str = "", raw: bool = False, max_industries_to_display: int = 15, min_pct_to_display_industry: float = 0.015, external_axes: Optional[List[matplotlib.axes._axes.Axes]] = None)
```

---

## Parameters

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| sector | str | Select sector to get number of companies by each industry | Technology | True |
| mktcap | str | Select market cap of companies to consider from Small, Mid and Large | Large | True |
| exclude_exchanges | bool | Exclude international exchanges | True | True |
| export | str | Format to export data as |  | True |
| raw | bool | Output all raw data | False | True |
| max_industries_to_display | int | Maximum number of industries to display | 15 | True |
| min_pct_to_display_industry | float | Minimum percentage to display industry | 0.015 | True |
| external_axes | Optional[List[plt.Axes]] | External axes (1 axis is expected in the list), by default None | None | True |


---

## Returns

This function does not return anything

---



</TabItem>
</Tabs>