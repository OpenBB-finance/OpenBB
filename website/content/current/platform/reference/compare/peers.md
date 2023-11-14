---
title: peers
description: Learn how to compare and analyze equity peers with the `obb.equity.compare.peers`
  function. This function allows you to retrieve a list of company peers based on
  symbol, sector, exchange, and market cap. Understand the parameters, returns, and
  data structure provided by this function.
keywords:
- equity peers
- company peers
- compare peers
- symbol
- provider
- parameter
- returns
- data
- list of peers
- sector
- exchange
- market cap
- serializable results
- chart object
- metadata
- command execution
- warnings
---


<!-- markdownlint-disable MD012 MD031 MD033 -->

import Tabs from '@theme/Tabs';
import TabItem from '@theme/TabItem';

Equity Peers. Company peers.

```python wordwrap
obb.equity.compare.peers(symbol: Union[str, List[str]], provider: Literal[str] = fmp)
```

---

## Parameters

<Tabs>
<TabItem value="standard" label="Standard">

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| symbol | Union[str, List[str]] | Symbol to get data for. |  | False |
| provider | Literal['fmp'] | The provider to use for the query, by default None. If None, the provider specified in defaults is selected or 'fmp' if there is no default. | fmp | True |
</TabItem>

</Tabs>

---

## Returns

```python wordwrap
OBBject
    results : List[EquityPeers]
        Serializable results.

    provider : Optional[Literal['fmp']]
        Provider name.

    warnings : Optional[List[Warning_]]
        List of warnings.

    chart : Optional[Chart]
        Chart object.

    metadata: Optional[Metadata]
        Metadata info about the command execution.
```

---

## Data

<Tabs>
<TabItem value="standard" label="Standard">

| Name | Type | Description |
| ---- | ---- | ----------- |
| peers_list | List[str] | A list of equity peers based on sector, exchange and market cap. |
</TabItem>

</Tabs>

