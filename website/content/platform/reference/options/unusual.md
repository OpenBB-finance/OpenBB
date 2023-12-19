---
title: unusual
description: Learn how to get the complete options chain for a ticker with the equity
  options unusual API. Explore the available parameters such as symbol and provider.
  Retrieve valuable data like the underlying symbol, contract symbol, trade type,
  sentiment, total value, total size, average price, ask/bid prices at execution,
  underlying price at execution, and timestamp.
keywords:
- complete options chain
- ticker options
- equity options unusual
- symbol
- provider
- intrinio
- source
- data
- underlying symbol
- contract symbol
- trade type
- sentiment
- total value
- total size
- average price
- ask at execution
- bid at execution
- underlying price at execution
- timestamp
---


<!-- markdownlint-disable MD012 MD031 MD033 -->

import Tabs from '@theme/Tabs';
import TabItem from '@theme/TabItem';

Get the complete options chain for a ticker.

```python wordwrap
obb.equity.options.unusual(symbol: Union[str, List[str]] = None, provider: Literal[str] = intrinio)
```

---

## Parameters

<Tabs>
<TabItem value="standard" label="Standard">

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| symbol | Union[str, List[str]] | Symbol to get data for. (the underlying symbol) | None | True |
| provider | Literal['intrinio'] | The provider to use for the query, by default None. If None, the provider specified in defaults is selected or 'intrinio' if there is no default. | intrinio | True |
</TabItem>

<TabItem value='intrinio' label='intrinio'>

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| symbol | Union[str, List[str]] | Symbol to get data for. (the underlying symbol) | None | True |
| provider | Literal['intrinio'] | The provider to use for the query, by default None. If None, the provider specified in defaults is selected or 'intrinio' if there is no default. | intrinio | True |
| source | Literal['delayed', 'realtime'] | The source of the data. Either realtime or delayed. | delayed | True |
</TabItem>

</Tabs>

---

## Returns

```python wordwrap
OBBject
    results : List[OptionsUnusual]
        Serializable results.

    provider : Optional[Literal['intrinio']]
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
| underlying_symbol | str | Symbol representing the entity requested in the data. (the underlying symbol) |
| contract_symbol | str | Contract symbol for the option. |
</TabItem>

<TabItem value='intrinio' label='intrinio'>

| Name | Type | Description |
| ---- | ---- | ----------- |
| underlying_symbol | str | Symbol representing the entity requested in the data. (the underlying symbol) |
| contract_symbol | str | Contract symbol for the option. |
| trade_type | str | The type of unusual trade. |
| sentiment | str | Bullish, Bearish, or Neutral Sentiment is estimated based on whether the trade was executed at the bid, ask, or mark price. |
| total_value | Union[int, float] | The aggregated value of all option contract premiums included in the trade. |
| total_size | int | The total number of contracts involved in a single transaction. |
| average_price | float | The average premium paid per option contract. |
| ask_at_execution | float | Ask price at execution. |
| bid_at_execution | float | Bid price at execution. |
| underlying_price_at_execution | float | Price of the underlying security at execution of trade. |
| timestamp | datetime | The UTC timestamp of order placement. |
</TabItem>

</Tabs>

