---
title: losers
description: OpenBB SDK Function
---

import Tabs from '@theme/Tabs';
import TabItem from '@theme/TabItem';

# losers

<Tabs>
<TabItem value="model" label="Model" default>

Shows Largest Losers - coins which lose the most in given period. [Source: CoinGecko]

Source Code: [[link](https://github.com/OpenBB-finance/OpenBBTerminal/tree/main/openbb_terminal/cryptocurrency/discovery/pycoingecko_model.py#L288)]

```python
openbb.crypto.disc.losers(interval: str = "1h", limit: int = 50, sortby: str = "market_cap_rank")
```

---

## Parameters

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| interval | str | Time interval by which data is displayed. One from [1h, 24h, 7d, 14d, 30d, 60d, 1y] | 1h | True |
| limit | int | Number of records to display | 50 | True |
| sortby | str | Key to sort data. The table can be sorted by every of its columns. Refer to<br/>API documentation (see /coins/markets in https://www.coingecko.com/en/api/documentation) | market_cap_rank | True |


---

## Returns

| Type | Description |
| ---- | ----------- |
| pd.DataFrame | Top Losers  - coins which lost most in price in given period of time.<br/>Columns: Symbol, Name, Volume, Price, %Change_{interval}, Url |
---



</TabItem>
<TabItem value="view" label="Chart">

Prints table showing Largest Losers - coins which lost the most in given period of time. [Source: CoinGecko]

Source Code: [[link](https://github.com/OpenBB-finance/OpenBBTerminal/tree/main/openbb_terminal/cryptocurrency/discovery/pycoingecko_view.py#L146)]

```python
openbb.crypto.disc.losers_chart(interval: str = "1h", limit: int = 20, export: str = "", sortby: str = "Market Cap Rank")
```

---

## Parameters

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| interval | str | Time period by which data is displayed. One from [1h, 24h, 7d, 14d, 30d, 60d, 1y] | 1h | True |
| limit | int | Number of records to display | 20 | True |
| sortby | str | Key to sort data. The table can be sorted by every of its columns. Refer to<br/>API documentation (see /coins/markets in https://www.coingecko.com/en/api/documentation) | Market Cap Rank | True |
| export | str | Export dataframe data to csv,json,xlsx file |  | True |


---

## Returns

This function does not return anything

---



</TabItem>
</Tabs>