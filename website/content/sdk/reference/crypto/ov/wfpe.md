---
title: wfpe
description: This page explains how to use OpenBB's wfpe function, which scrapes coin
  withdrawal fees per exchange and presents them visually or in data format. It provides
  detailed parameters and returns information for both the model and view aspects
  of the function.
keywords:
- wfpe function
- coin withdrawal fees
- crypto exchange
- data scraping
- data visualization
- parameters
- returns
- Model
- View
---

import HeadTitle from '@site/src/components/General/HeadTitle.tsx';

<HeadTitle title="crypto.ov.wfpe - Reference | OpenBB SDK Docs" />

import Tabs from '@theme/Tabs';
import TabItem from '@theme/TabItem';

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
