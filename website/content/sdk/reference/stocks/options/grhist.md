---
title: grhist
description: OpenBB SDK Function
---

import Tabs from '@theme/Tabs';
import TabItem from '@theme/TabItem';

# grhist

<Tabs>
<TabItem value="model" label="Model" default>

Get histoical option greeks

Source Code: [[link](https://github.com/OpenBB-finance/OpenBBTerminal/tree/main/openbb_terminal/stocks/options/screen/syncretism_model.py#L37)]

```python
openbb.stocks.options.grhist(symbol: str, expiry: str, strike: Union[str, float], chain_id: str = "", put: bool = False)
```

---

## Parameters

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| symbol | str | Stock ticker symbol | None | False |
| expiry | str | Option expiration date | None | False |
| strike | Union[str, float] | Strike price to look for | None | False |
| chain_id | str | OCC option symbol.  Overwrites other inputs |  | True |
| put | bool | Is this a put option? | False | True |


---

## Returns

| Type | Description |
| ---- | ----------- |
| pd.DataFrame | Dataframe containing historical greeks |
---



</TabItem>
<TabItem value="view" label="Chart">

Plots historical greeks for a given option. [Source: Syncretism]

Source Code: [[link](https://github.com/OpenBB-finance/OpenBBTerminal/tree/main/openbb_terminal/stocks/options/screen/syncretism_view.py#L107)]

```python
openbb.stocks.options.grhist_chart(symbol: str, expiry: str, strike: Union[float, str], greek: str = "Delta", chain_id: str = "", put: bool = False, raw: bool = False, limit: Union[int, str] = 20, export: str = "", external_axes: Optional[List[matplotlib.axes._axes.Axes]] = None)
```

---

## Parameters

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| symbol | str | Stock ticker | None | False |
| expiry | str | Expiration date | None | False |
| strike | Union[str, float] | Strike price to consider | None | False |
| greek | str | Greek variable to plot | Delta | True |
| chain_id | str | OCC option chain.  Overwrites other variables |  | True |
| put | bool | Is this a put option? | False | True |
| raw | bool | Print to console | False | True |
| limit | int | Number of rows to show in raw | 20 | True |
| export | str | Format to export data |  | True |
| external_axes | Optional[List[plt.Axes]] | External axes (1 axis is expected in the list), by default None | None | True |


---

## Returns

This function does not return anything

---



</TabItem>
</Tabs>