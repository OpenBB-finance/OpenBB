---
title: Stock Peers
description: The documentation gives an overview about the 'StockPeers', 'StockPeersData'
  and 'StockPeersQueryParams' of openbb_provider package. It elaborates the parameters
  such as 'symbol' and 'provider', and provides details about the types and functions
  of the 'stock_peers' class.
keywords:
- StockPeers
- stock_peers
- StockPeersData
- StockPeersQueryParams
- symbol
- provider
- fmp
- peers_list
- openbb_provider
---

import HeadTitle from '@site/src/components/General/HeadTitle.tsx';

<HeadTitle title="Stock Peers - Data_Models | OpenBB Platform Docs" />


import Tabs from '@theme/Tabs';
import TabItem from '@theme/TabItem';


---

## Implementation details

### Class names

| Model name | Parameters class | Data class |
| ---------- | ---------------- | ---------- |
| `StockPeers` | `StockPeersQueryParams` | `StockPeersData` |

### Import Statement

```python
from openbb_provider.standard_models.stock_peers import (
StockPeersData,
StockPeersQueryParams,
)
```

## Parameters

<Tabs>
<TabItem value="standard" label="Standard">

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| symbol | Union[str, List[str]] | Symbol to get data for. |  | False |
| provider | Literal['fmp'] | The provider to use for the query, by default None. If None, the provider specified in defaults is selected or 'fmp' if there is no default. | fmp | True |
</TabItem>

</Tabs>

## Data

<Tabs>
<TabItem value="standard" label="Standard">

| Name | Type | Description |
| ---- | ---- | ----------- |
| symbol | str | Symbol representing the entity requested in the data. |
| peers_list | List[str] | A list of stock peers based on sector, exchange and market cap. |
</TabItem>

</Tabs>
