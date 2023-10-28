---
title: peers
description: This documentation page provides detailed information about stock peers
  including the market sector, exchange and market cap. The data is provided by the
  'fmp' provider and includes metadata about the command execution.
keywords:
- stock market
- stock peers
- finance
- fmp
- data provider
- stock metadata
- symbol
- market sector
- market cap
- exchange
---

import HeadTitle from '@site/src/components/General/HeadTitle.tsx';

<HeadTitle title="peers - Ca - Reference | OpenBB Platform Docs" />

import Tabs from '@theme/Tabs';
import TabItem from '@theme/TabItem';

# peers

Stock Peers. Company peers.

```python wordwrap
peers(symbol: Union[str, List[str]], provider: Literal[str] = fmp)
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
    results : List[StockPeers]
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
| symbol | str | Symbol representing the entity requested in the data. |
| peers_list | List[str] | A list of stock peers based on sector, exchange and market cap. |
</TabItem>

</Tabs>
