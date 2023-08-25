---
title: ttcp
description: OpenBB SDK Function
---

import Tabs from '@theme/Tabs';
import TabItem from '@theme/TabItem';

# ttcp

<Tabs>
<TabItem value="model" label="Model" default>

Get most traded crypto pairs on given decentralized exchange in chosen time period.

Source Code: [[link](https://github.com/OpenBB-finance/OpenBBTerminal/tree/main/openbb_terminal/cryptocurrency/onchain/bitquery_model.py#L658)]

```python
openbb.crypto.onchain.ttcp(network: str = "ethereum", exchange: str = "Uniswap", limit: int = 90, sortby: str = "tradeAmount", ascend: bool = True)
```

---

## Parameters

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| network | str | EVM network. One from list: bsc (binance smart chain), ethereum or matic | ethereum | True |
| exchange | st | Decentralized exchange name | Uniswap | True |
| limit | int | Number of days taken into calculation account. | 90 | True |
| sortby | str | Key by which to sort data | tradeAmount | True |
| ascend | bool | Flag to sort data ascending | True | True |


---

## Returns

| Type | Description |
| ---- | ----------- |
| pd.DataFrame | Most traded crypto pairs on given decentralized exchange in chosen time period. |
---



</TabItem>
<TabItem value="view" label="Chart">

Prints table showing most traded crypto pairs on given decentralized exchange in chosen time period.

Source Code: [[link](https://github.com/OpenBB-finance/OpenBBTerminal/tree/main/openbb_terminal/cryptocurrency/onchain/bitquery_view.py#L286)]

```python
openbb.crypto.onchain.ttcp_chart(exchange: str = "Uniswap", days: int = 10, limit: int = 10, sortby: str = "tradeAmount", ascend: bool = True, export: str = "")
```

---

## Parameters

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| exchange | str | Decentralized exchange name | Uniswap | True |
| days | int | Number of days taken into calculation account. | 10 | True |
| sortby | str | Key by which to sort data | tradeAmount | True |
| ascend | bool | Flag to sort data ascending | True | True |
| export | str | Export dataframe data to csv,json,xlsx file |  | True |


---

## Returns

| Type | Description |
| ---- | ----------- |
| pd.DataFrame | Most traded crypto pairs on given decentralized exchange in chosen time period. |
---



</TabItem>
</Tabs>