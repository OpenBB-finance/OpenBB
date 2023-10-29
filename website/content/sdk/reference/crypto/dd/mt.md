---
title: mt
description: The page includes details about different functions used in cryptocurrency
  due diligence, specifically handling and plotting Messari timeseries data. This
  includes parameters and return values for each function, including the crypto symbol,
  timeseries_id, interval frequency, start and end date. Also discusses exporting
  these dataframes and using matplotlib for visualizing data.
keywords:
- messari_timeseries
- crypto_symbol
- timeseries_id
- start_date
- end_date
- interval_frequency
- export_dataframe
- cryptocurrency_due_diligence
- openbb_terminal
- OpenBB-finance
- matplotlib
---

import HeadTitle from '@site/src/components/General/HeadTitle.tsx';

<HeadTitle title="crypto.dd.mt - Reference | OpenBB SDK Docs" />

import Tabs from '@theme/Tabs';
import TabItem from '@theme/TabItem';

<Tabs>
<TabItem value="model" label="Model" default>

Returns messari timeseries

Source Code: [[link](https://github.com/OpenBB-finance/OpenBBTerminal/tree/main/openbb_terminal/cryptocurrency/due_diligence/messari_model.py#L124)]

```python
openbb.crypto.dd.mt(symbol: str, timeseries_id: str, interval: str = "1d", start_date: Optional[str] = None, end_date: Optional[str] = None)
```

---

## Parameters

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| symbol | str | Crypto symbol to check messari timeseries | None | False |
| timeseries_id | str | Messari timeserie id | None | False |
| interval | str | Interval frequency (possible values are: 5m, 15m, 30m, 1h, 1d, 1w) | 1d | True |
| start | Optional[str] | Initial date like string (e.g., 2021-10-01) | None | True |
| end | Optional[str] | End date like string (e.g., 2021-10-01) | None | True |


---

## Returns

| Type | Description |
| ---- | ----------- |
| Tuple[pd.DataFrame, str] | Messari timeseries over time,<br/>Timeseries title |
---

</TabItem>
<TabItem value="view" label="Chart">

Plots messari timeseries

Source Code: [[link](https://github.com/OpenBB-finance/OpenBBTerminal/tree/main/openbb_terminal/cryptocurrency/due_diligence/messari_view.py#L103)]

```python
openbb.crypto.dd.mt_chart(symbol: str, timeseries_id: str, start_date: Optional[str] = None, end_date: Optional[str] = None, interval: str = "1d", export: str = "", external_axes: Optional[List[matplotlib.axes._axes.Axes]] = None)
```

---

## Parameters

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| symbol | str | Crypto symbol to check market cap dominance | None | False |
| timeseries_id | str | Obtained by api.crypto.dd.get_mt command | None | False |
| start_date | Optional[str] | Initial date like string (e.g., 2021-10-01) | None | True |
| end_date | Optional[str] | End date like string (e.g., 2021-10-01) | None | True |
| interval | str | Interval frequency (possible values are: 5m, 15m, 30m, 1h, 1d, 1w) | 1d | True |
| export | str | Export dataframe data to csv,json,xlsx file |  | True |
| external_axes | Optional[List[plt.Axes]] | External axes (1 axis is expected in the list), by default None | None | True |


---

## Returns

This function does not return anything

---

</TabItem>
</Tabs>
