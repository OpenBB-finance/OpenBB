---
title: "constituents"
description: "Learn how to fetch constituents of an index using the OBB library in  Python. Get detailed information such as symbol, name, sector, sub-sector, headquarters,  date of first addition, CIK, and founding year of the constituent companies in the  index."
keywords:
- index constituents
- fetch constituents
- index constituents parameters
- index constituents returns
- index constituents data
- index constituents symbol
- index constituents name
- index constituents sector
- index constituents sub-sector
- index constituents headquarters
- index constituents date first added
- index constituents cik
- index constituents founding year
---

import HeadTitle from '@site/src/components/General/HeadTitle.tsx';

<HeadTitle title="index/constituents - Reference | OpenBB Platform Docs" />

<!-- markdownlint-disable MD012 MD031 MD033 -->

import Tabs from '@theme/Tabs';
import TabItem from '@theme/TabItem';

Index Constituents.


Examples
--------

```python
from openbb import obb
obb.index.constituents(symbol='dowjones', provider='fmp')
# Providers other than FMP will use the ticker symbol.
obb.index.constituents(symbol='BEP50P', provider='cboe')
```

---

## Parameters

<Tabs>

<TabItem value='standard' label='standard'>

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| symbol | str | Symbol to get data for. |  | False |
| provider | Literal['cboe', 'fmp', 'tmx'] | The provider to use for the query, by default None. If None, the provider specified in defaults is selected or 'cboe' if there is no default. | cboe | True |
</TabItem>

<TabItem value='cboe' label='cboe'>

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| symbol | str | Symbol to get data for. |  | False |
| provider | Literal['cboe', 'fmp', 'tmx'] | The provider to use for the query, by default None. If None, the provider specified in defaults is selected or 'cboe' if there is no default. | cboe | True |
</TabItem>

<TabItem value='fmp' label='fmp'>

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| symbol | str | Symbol to get data for. |  | False |
| provider | Literal['cboe', 'fmp', 'tmx'] | The provider to use for the query, by default None. If None, the provider specified in defaults is selected or 'cboe' if there is no default. | cboe | True |
</TabItem>

<TabItem value='tmx' label='tmx'>

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| symbol | str | Symbol to get data for. |  | False |
| provider | Literal['cboe', 'fmp', 'tmx'] | The provider to use for the query, by default None. If None, the provider specified in defaults is selected or 'cboe' if there is no default. | cboe | True |
| use_cache | bool | Whether to use a cached request. Index data is from a single JSON file, updated each day after close. It is cached for one day. To bypass, set to False. | True | True |
</TabItem>

</Tabs>

---

## Returns

```python wordwrap
OBBject
    results : IndexConstituents
        Serializable results.
    provider : Literal['cboe', 'fmp', 'tmx']
        Provider name.
    warnings : Optional[List[Warning_]]
        List of warnings.
    chart : Optional[Chart]
        Chart object.
    extra : Dict[str, Any]
        Extra info.

```

---

## Data

<Tabs>

<TabItem value='standard' label='standard'>

| Name | Type | Description |
| ---- | ---- | ----------- |
| symbol | str | Symbol representing the entity requested in the data. |
| name | str | Name of the constituent company in the index. |
</TabItem>

<TabItem value='cboe' label='cboe'>

| Name | Type | Description |
| ---- | ---- | ----------- |
| symbol | str | Symbol representing the entity requested in the data. |
| name | str | Name of the constituent company in the index. |
| security_type | str | The type of security represented. |
| last_price | float | Last price for the symbol. |
| open | float | The open price. |
| high | float | The high price. |
| low | float | The low price. |
| close | float | The close price. |
| volume | int | The trading volume. |
| prev_close | float | The previous close price. |
| change | float | Change in price. |
| change_percent | float | Change in price as a normalized percentage. |
| tick | str | Whether the last sale was an up or down tick. |
| last_trade_time | datetime | Last trade timestamp for the symbol. |
| asset_type | str | Type of asset. |
</TabItem>

<TabItem value='fmp' label='fmp'>

| Name | Type | Description |
| ---- | ---- | ----------- |
| symbol | str | Symbol representing the entity requested in the data. |
| name | str | Name of the constituent company in the index. |
| sector | str | Sector the constituent company in the index belongs to. |
| sub_sector | str | Sub-sector the constituent company in the index belongs to. |
| headquarter | str | Location of the headquarter of the constituent company in the index. |
| date_first_added | Union[str, date] | Date the constituent company was added to the index. |
| cik | int | Central Index Key (CIK) for the requested entity. |
| founded | Union[str, date] | Founding year of the constituent company in the index. |
</TabItem>

<TabItem value='tmx' label='tmx'>

| Name | Type | Description |
| ---- | ---- | ----------- |
| symbol | str | Symbol representing the entity requested in the data. |
| name | str | Name of the constituent company in the index. |
| market_value | float | The quoted market value of the asset. |
</TabItem>

</Tabs>

