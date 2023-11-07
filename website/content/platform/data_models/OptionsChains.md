---
title: Get the complete options chain for a ticker
description: This documentation page details the implementation of OptionsChains,
  including class names, import statements, parameters, and data. It explains various
  aspects such as contract symbols, expiration dates, strike prices and more. This
  resource is especially beneficial for users interested in options trading data and
  how to query them using the openbb_provider python package.
keywords:
- OptionsChains
- OptionsChainsQueryParams
- OptionsChainsData
- parameters
- data
- contract symbol
- symbol
- expiration date
- strike price
- call or put
- class names
- implementation details
- python
- openbb_provider
- intrinio
- date
- provider
- open interest
- implied volatility
- delta
- gamma
- theta
- vega
---

import HeadTitle from '@site/src/components/General/HeadTitle.tsx';

<HeadTitle title="Get the complete options chain for a ticker - Data_Models | OpenBB Platform Docs" />


import Tabs from '@theme/Tabs';
import TabItem from '@theme/TabItem';


---

## Implementation details

### Class names

| Model name | Parameters class | Data class |
| ---------- | ---------------- | ---------- |
| `OptionsChains` | `OptionsChainsQueryParams` | `OptionsChainsData` |

### Import Statement

```python
from openbb_provider.standard_models.options_chains import (
OptionsChainsData,
OptionsChainsQueryParams,
)
```

## Parameters

<Tabs>
<TabItem value="standard" label="Standard">

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| symbol | Union[str, List[str]] | Symbol to get data for. |  | False |
| provider | Literal['intrinio'] | The provider to use for the query, by default None. If None, the provider specified in defaults is selected or 'intrinio' if there is no default. | intrinio | True |
</TabItem>

<TabItem value='intrinio' label='intrinio'>

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| symbol | Union[str, List[str]] | Symbol to get data for. |  | False |
| provider | Literal['intrinio'] | The provider to use for the query, by default None. If None, the provider specified in defaults is selected or 'intrinio' if there is no default. | intrinio | True |
| date | str | Date for which the options chains are returned. |  | False |
</TabItem>

</Tabs>

## Data

<Tabs>
<TabItem value="standard" label="Standard">

| Name | Type | Description |
| ---- | ---- | ----------- |
| contract_symbol | str | Contract symbol for the option. |
| symbol | str | Underlying symbol for the option. |
| expiration | date | Expiration date of the contract. |
| strike | float | Strike price of the contract. |
| type | str | Call or Put. |
| date | date | Date for which the options chains are returned. |
| close | float | Close price for the option that day. |
| close_bid | float | The closing bid price for the option that day. |
| close_ask | float | The closing ask price for the option that day. |
| volume | float | Current trading volume on the contract. |
| open | float | Opening price of the option. |
| open_bid | float | The opening bid price for the option that day. |
| open_ask | float | The opening ask price for the option that day. |
| open_interest | float | Open interest on the contract. |
| high | float | High price of the option. |
| low | float | Low price of the option. |
| mark | float | The mid-price between the latest bid-ask spread. |
| ask_high | float | The highest ask price for the option that day. |
| ask_low | float | The lowest ask price for the option that day. |
| bid_high | float | The highest bid price for the option that day. |
| bid_low | float | The lowest bid price for the option that day. |
| implied_volatility | float | Implied volatility of the option. |
| delta | float | Delta of the option. |
| gamma | float | Gamma of the option. |
| theta | float | Theta of the option. |
| vega | float | Vega of the option. |
</TabItem>

</Tabs>
