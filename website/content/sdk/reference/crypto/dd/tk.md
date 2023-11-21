---
title: tk
description: This page provides documentation for the tk model and chart functions
  from the openbb.crypto.dd library. The model function returns coin tokenomics for
  a specific cryptocurrency while the chart function plots the same.
keywords:
- cryptocurrency
- tokenomics
- openbb.crypto.dd
- coin tokenomics
- coin tokenomics plot
- programming
- function documentation
---

import HeadTitle from '@site/src/components/General/HeadTitle.tsx';

<HeadTitle title="crypto.dd.tk - Reference | OpenBB SDK Docs" />

import Tabs from '@theme/Tabs';
import TabItem from '@theme/TabItem';

<Tabs>
<TabItem value="model" label="Model" default>

Returns coin tokenomics

Source Code: [[link](https://github.com/OpenBB-finance/OpenBBTerminal/tree/main/openbb_terminal/cryptocurrency/due_diligence/messari_model.py#L283)]

```python
openbb.crypto.dd.tk(symbol: str, coingecko_id: str)
```

---

## Parameters

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| symbol | str | Crypto symbol to check tokenomics | None | False |
| coingecko_id | str | ID from coingecko | None | False |


---

## Returns

| Type | Description |
| ---- | ----------- |
| Tuple[pd.DataFrame, pd.DataFrame] | Metric Value tokenomics,<br/>Circulating supply overtime |
---

</TabItem>
<TabItem value="view" label="Chart">

Plots coin tokenomics

Source Code: [[link](https://github.com/OpenBB-finance/OpenBBTerminal/tree/main/openbb_terminal/cryptocurrency/due_diligence/messari_view.py#L386)]

```python
openbb.crypto.dd.tk_chart(symbol: str, export: str = "", external_axes: Optional[List[matplotlib.axes._axes.Axes]] = None)
```

---

## Parameters

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| symbol | str | Crypto symbol to check tokenomics | None | False |
| export | str | Export dataframe data to csv,json,xlsx file |  | True |
| external_axes | Optional[List[plt.Axes]] | External axes (2 axes are expected in the list), by default None | None | True |


---

## Returns

This function does not return anything

---

</TabItem>
</Tabs>
