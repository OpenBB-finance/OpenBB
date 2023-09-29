---
title: oi
description: OpenBB SDK Function
---

import Tabs from '@theme/Tabs';
import TabItem from '@theme/TabItem';

# oi

<Tabs>
<TabItem value="model" label="Model" default>

Returns open interest by exchange for a certain symbol

Source Code: [[link](https://github.com/OpenBB-finance/OpenBBTerminal/tree/main/openbb_terminal/cryptocurrency/due_diligence/coinglass_model.py#L148)]

```python
openbb.crypto.dd.oi(symbol: str, interval: int = 0)
```

---

## Parameters

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| symbol | str | Crypto Symbol to search open interest futures (e.g., BTC) | None | False |
| interval | int | Frequency (possible values are: 0 for ALL, 2 for 1H, 1 for 4H, 4 for 12H), by default 0 | 0 | True |


---

## Returns

| Type | Description |
| ---- | ----------- |
| pd.DataFrame | open interest by exchange and price |
---



</TabItem>
<TabItem value="view" label="Chart">

Plots open interest by exchange for a certain cryptocurrency

Source Code: [[link](https://github.com/OpenBB-finance/OpenBBTerminal/tree/main/openbb_terminal/cryptocurrency/due_diligence/coinglass_view.py#L55)]

```python
openbb.crypto.dd.oi_chart(symbol: str, interval: int = 0, export: str = "")
```

---

## Parameters

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| symbol | str | Crypto symbol to search open interest (e.g., BTC) | None | False |
| interval | int | Frequency (possible values are: 0 for ALL, 2 for 1H, 1 for 4H, 4 for 12H), by default 0 | 0 | True |
| export | str | Export dataframe data to csv,json,xlsx file |  | True |


---

## Returns

This function does not return anything

---



</TabItem>
</Tabs>