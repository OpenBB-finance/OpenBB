---
title: wfpe
description: OpenBB SDK Function
---

import Tabs from '@theme/Tabs';
import TabItem from '@theme/TabItem';

# wfpe

<Tabs>
<TabItem value="model" label="Model" default>

Scrapes coin withdrawal fees per exchange

Source Code: [[link](https://github.com/OpenBB-finance/OpenBBTerminal/tree/main/openbb_terminal/cryptocurrency/overview/withdrawalfees_model.py#L207)]

```python
openbb.crypto.ov.wfpe(symbol: str)
```

---

## Parameters

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| symbol | str | Coin to check withdrawal fees. By default bitcoin | None | False |


---

## Returns

| Type | Description |
| ---- | ----------- |
| List | - str: Overall statistics (exchanges, lowest, average and median)<br/>- pd.DataFrame: Exchange, Withdrawal Fee, Minimum Withdrawal Amount |
---



</TabItem>
<TabItem value="view" label="Chart">

Coin withdrawal fees per exchange

Source Code: [[link](https://github.com/OpenBB-finance/OpenBBTerminal/tree/main/openbb_terminal/cryptocurrency/overview/withdrawalfees_view.py#L86)]

```python
openbb.crypto.ov.wfpe_chart(symbol: str, export: str = "")
```

---

## Parameters

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| symbol | str | Coin to check withdrawal fees | None | False |
| export | str | Export dataframe data to csv,json,xlsx file |  | True |


---

## Returns

This function does not return anything

---



</TabItem>
</Tabs>