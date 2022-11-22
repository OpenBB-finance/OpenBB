---
title: anchor_data
description: OpenBB SDK Function
---

import Tabs from '@theme/Tabs';
import TabItem from '@theme/TabItem';

# anchor_data

<Tabs>
<TabItem value="model" label="Model" default>

Returns anchor protocol earnings data of a certain terra address

Source Code: [[link](https://github.com/OpenBB-finance/OpenBBTerminal/tree/main/openbb_terminal/cryptocurrency/defi/cryptosaurio_model.py#L17)]

```python
openbb.crypto.defi.anchor_data(address: str = "")
```

---

## Parameters

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| address | str | Terra address. Valid terra addresses start with 'terra' |  | True |


---

## Returns

| Type | Description |
| ---- | ----------- |
| Tuple[pd.DataFrame, pd.DataFrame, str] | - pd.DataFrame: Earnings over time in UST<br/>- pd.DataFrame: History of transactions<br/>- str:              Overall statistics |
---



</TabItem>
<TabItem value="view" label="Chart">

Plots anchor protocol earnings data of a certain terra address

Source Code: [[link](https://github.com/OpenBB-finance/OpenBBTerminal/tree/main/openbb_terminal/cryptocurrency/defi/cryptosaurio_view.py#L25)]

```python
openbb.crypto.defi.anchor_data_chart(address: str = "", export: str = "", show_transactions: bool = False, external_axes: Optional[List[matplotlib.axes._axes.Axes]] = None)
```

---

## Parameters

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| asset | str | Terra asset {ust,luna,sdt} | None | True |
| address | str | Terra address. Valid terra addresses start with 'terra' |  | True |
| show_transactions | bool | Flag to show history of transactions in Anchor protocol for address. Default False | False | True |
| export | str | Export dataframe data to csv,json,xlsx file |  | True |
| external_axes | Optional[List[plt.Axes]] | External axes (1 axis is expected in the list), by default None | None | True |


---

## Returns

This function does not return anything

---



</TabItem>
</Tabs>