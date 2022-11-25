---
title: hr
description: OpenBB SDK Function
---

import Tabs from '@theme/Tabs';
import TabItem from '@theme/TabItem';

# hr

<Tabs>
<TabItem value="model" label="Model" default>

Returns dataframe with mean hashrate of btc or eth blockchain and symbol price

Source Code: [[link](https://github.com/OpenBB-finance/OpenBBTerminal/tree/main/openbb_terminal/cryptocurrency/due_diligence/glassnode_model.py#L375)]

```python
openbb.crypto.onchain.hr(symbol: str, interval: str = "24h", start_date: str = "2010-01-01", end_date: Optional[str] = None)
```

---

## Parameters

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| symbol | str | Blockchain to check hashrate (BTC or ETH) | None | False |
| start_date | str | Initial date, format YYYY-MM-DD | 2010-01-01 | True |
| end_date | str | Final date, format YYYY-MM-DD | None | True |
| interval | str | Interval frequency (e.g., 24h) | 24h | True |


---

## Returns

| Type | Description |
| ---- | ----------- |
| pd.DataFrame | mean hashrate and symbol price over time |
---



</TabItem>
<TabItem value="view" label="Chart">

Plots dataframe with mean hashrate of btc or eth blockchain and symbol price.

Source Code: [[link](https://github.com/OpenBB-finance/OpenBBTerminal/tree/main/openbb_terminal/cryptocurrency/due_diligence/glassnode_view.py#L320)]

```python
openbb.crypto.onchain.hr_chart(symbol: str, start_date: str = "2010-01-01", end_date: Optional[str] = None, interval: str = "24h", export: str = "", external_axes: Optional[List[matplotlib.axes._axes.Axes]] = None)
```

---

## Parameters

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| symbol | str | Blockchain to check mean hashrate (BTC or ETH) | None | False |
| start_date | str | Initial date, format YYYY-MM-DD | 2010-01-01 | True |
| end_date | Optional[str] | Final date, format YYYY-MM-DD | None | True |
| interval | str | Interval frequency (possible values are: 24, 1w, 1month) | 24h | True |
| export | str | Export dataframe data to csv,json,xlsx file |  | True |
| external_axes | Optional[List[plt.Axes]] | External axes (2 axes are expected in the list), by default None | None | True |


---

## Returns

This function does not return anything

---



</TabItem>
</Tabs>