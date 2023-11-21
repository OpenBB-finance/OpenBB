---
title: aterra
description: This document provides information about how to fetch historical data
  for a specific Terra asset, plot the 30-day history of that asset and explains the
  usage of each function. Also includes source code links.
keywords:
- Terra assets
- historical data
- address
- GET request
- Draw chart
- aterra
- meta data
- parameters
- returns
---

import HeadTitle from '@site/src/components/General/HeadTitle.tsx';

<HeadTitle title="crypto.defi.aterra - Reference | OpenBB SDK Docs" />

import Tabs from '@theme/Tabs';
import TabItem from '@theme/TabItem';

<Tabs>
<TabItem value="model" label="Model" default>

Returns historical data of an asset in a certain terra address

Source Code: [[link](https://github.com/OpenBB-finance/OpenBBTerminal/tree/main/openbb_terminal/cryptocurrency/defi/terraengineer_model.py#L19)]

```python wordwrap
openbb.crypto.defi.aterra(asset: str = "ust", address: str = "terra1tmnqgvg567ypvsvk6rwsga3srp7e3lg6u0elp8")
```

---

## Parameters

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| asset | str | Terra asset {ust,luna,sdt} | ust | True |
| address | str | Terra address. Valid terra addresses start with 'terra' | terra1tmnqgvg567ypvsvk6rwsga3srp7e3lg6u0elp8 | True |


---

## Returns

| Type | Description |
| ---- | ----------- |
| pd.DataFrame | historical data |
---



</TabItem>
<TabItem value="view" label="Chart">

Plots the 30-day history of specified asset in terra address

Source Code: [[link](https://github.com/OpenBB-finance/OpenBBTerminal/tree/main/openbb_terminal/cryptocurrency/defi/terraengineer_view.py#L18)]

```python wordwrap
openbb.crypto.defi.aterra_chart(asset: str = "", address: str = "", export: str = "", sheet_name: Optional[str] = None, external_axes: bool = False)
```

---

## Parameters

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| asset | str | Terra asset {ust,luna,sdt} |  | True |
| address | str | Terra address. Valid terra addresses start with 'terra' |  | True |
| export | str | Export dataframe data to csv,json,xlsx file |  | True |
| external_axes | bool | Whether to return the figure object or not, by default False | False | True |


---

## Returns

This function does not return anything

---



</TabItem>
</Tabs>