---
title: headlines
description: OpenBB SDK Function
---

import Tabs from '@theme/Tabs';
import TabItem from '@theme/TabItem';

# headlines

<Tabs>
<TabItem value="model" label="Model" default>

Gets Sentiment analysis provided by FinBrain's API [Source: finbrain].

Source Code: [[link](https://github.com/OpenBB-finance/OpenBBTerminal/tree/main/openbb_terminal/common/behavioural_analysis/finbrain_model.py#L15)]

```python
openbb.crypto.dd.headlines(symbol: str)
```

---

## Parameters

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| symbol | str | Ticker symbol to get the sentiment analysis from | None | False |


---

## Returns

| Type | Description |
| ---- | ----------- |
| pd.DataFrame | Empty if there was an issue with data retrieval |
---



</TabItem>
<TabItem value="view" label="Chart">

Sentiment analysis from FinBrain for Cryptocurrencies

Source Code: [[link](https://github.com/OpenBB-finance/OpenBBTerminal/tree/main/openbb_terminal/cryptocurrency/due_diligence/finbrain_crypto_view.py#L39)]

```python
openbb.crypto.dd.headlines_chart(symbol: str, raw: bool = False, export: str = "", external_axes: Optional[List[matplotlib.axes._axes.Axes]] = None)
```

---

## Parameters

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| symbol | str | Cryptocurrency | None | False |
| raw | False | Display raw table data | False | True |
| export | str | Export dataframe data to csv,json,xlsx file |  | True |
| external_axes | Optional[List[plt.Axes]] | External axes (1 axis is expected in the list), by default None | None | True |


---

## Returns

This function does not return anything

---



</TabItem>
</Tabs>