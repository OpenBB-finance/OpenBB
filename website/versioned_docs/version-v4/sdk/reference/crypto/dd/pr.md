---
title: pr
description: OpenBB SDK Function
---

import Tabs from '@theme/Tabs';
import TabItem from '@theme/TabItem';

# pr

<Tabs>
<TabItem value="model" label="Model" default>

Fetch data to calculate potential returns of a certain coin. [Source: CoinGecko]

Source Code: [[link](https://github.com/OpenBB-finance/OpenBBTerminal/tree/main/openbb_terminal/cryptocurrency/due_diligence/pycoingecko_model.py#L63)]

```python
openbb.crypto.dd.pr(main_coin: str, to_symbol: Optional[str] = None, limit: Optional[int] = None, price: Optional[int] = None)
```

---

## Parameters

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| main_coin | str | Coin loaded to check potential returns for (e.g., algorand) | None | False |
| to_symbol | str | None | Coin to compare main_coin with (e.g., bitcoin) | None | True |
| limit | int | None | Number of coins with highest market cap to compare main_coin with (e.g., 5) | None | True |
| price | None | Target price of main_coin to check potential returns (e.g., 5) | None | True |


---

## Returns

| Type | Description |
| ---- | ----------- |
| pd.DataFrame | Potential returns data<br/>Columns: Coin, Current Price, Target Coin, Potential Price, Potential Market Cap ($), Change (%) |
---



</TabItem>
<TabItem value="view" label="Chart">

Prints table showing potential returns of a certain coin. [Source: CoinGecko]

Source Code: [[link](https://github.com/OpenBB-finance/OpenBBTerminal/tree/main/openbb_terminal/cryptocurrency/due_diligence/pycoingecko_view.py#L20)]

```python
openbb.crypto.dd.pr_chart(to_symbol: str, from_symbol: Optional[str] = None, limit: Optional[int] = None, price: Optional[int] = None, export: str = "")
```

---

## Parameters

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| to_symbol | str | Coin loaded to check potential returns for (e.g., algorand) | None | False |
| from_symbol | str | None | Coin to compare main_coin with (e.g., bitcoin) | None | True |
| limit | int | None | Number of coins with highest market cap to compare main_coin with (e.g., 5) | None | True |
| price | None | Target price of main_coin to check potential returns (e.g., 5) | None | True |
| export | str | Export dataframe data to csv,json,xlsx file |  | True |


---

## Returns

This function does not return anything

---



</TabItem>
</Tabs>