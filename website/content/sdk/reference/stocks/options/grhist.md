---
title: grhist
description: Learn about using the functions grhist, syncretism model, and syncretism
  view in OpenBBTerminal to get historical greeks for options on stocks. These Python
  functions are clearly explained and the source code is provided for in-depth understanding.
  The page also delineates parameters and return values.
keywords:
- stocks
- options
- grhist
- syncretism model
- historical greeks
- strike price
- put option
- OCC option symbol
- grhist chart
- Greek variable
- export data
---

import HeadTitle from '@site/src/components/General/HeadTitle.tsx';

<HeadTitle title="stocks.options.grhist - Reference | OpenBB SDK Docs" />

import Tabs from '@theme/Tabs';
import TabItem from '@theme/TabItem';

<Tabs>
<TabItem value="model" label="Model" default>

Get historical EOD option prices, with Greeks, for a given OCC chain label.

Source Code: [[link](https://github.com/OpenBB-finance/OpenBBTerminal/tree/main/openbb_terminal/stocks/options/intrinio_model.py#L345)]

```python wordwrap
openbb.stocks.options.grhist(symbol: str)
```

---

## Parameters

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| symbol | str | Symbol to get historical option chain for.  Should be an OCC chain label. | None | False |


---

## Returns

| Type | Description |
| ---- | ----------- |
| pd.DataFrame | Dataframe of historical option chain. |
---



</TabItem>
<TabItem value="view" label="Chart">

Plots historical greeks for a given option.

Source Code: [[link](https://github.com/OpenBB-finance/OpenBBTerminal/tree/main/openbb_terminal/stocks/options/intrinio_view.py#L115)]

```python wordwrap
openbb.stocks.options.grhist_chart(symbol: str = "", expiry: str = "", strike: Union[float, str] = 0, greek: str = "Delta", chain_id: str = "", put: bool = False, raw: bool = False, limit: Union[int, str] = 20, export: str = "", sheet_name: Optional[str] = None, external_axes: bool = False)
```

---

## Parameters

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| symbol | str | Stock ticker |  | True |
| expiry | str | Expiration date |  | True |
| strike | Union[str, float] | Strike price to consider | 0 | True |
| greek | str | Greek variable to plot | Delta | True |
| chain_id | str | OCC option chain.  Overwrites other variables |  | True |
| put | bool | Is this a put option? | False | True |
| raw | bool | Print to console | False | True |
| limit | int | Number of rows to show in raw | 20 | True |
| sheet_name | str | Optionally specify the name of the sheet the data is exported to. | None | True |
| export | str | Format to export data |  | True |
| external_axes | bool | Whether to return the figure object or not, by default False | False | True |


---

## Returns

This function does not return anything

---



</TabItem>
</Tabs>