---
title: chains
description: OpenBB Platform Function
---

import Tabs from '@theme/Tabs';
import TabItem from '@theme/TabItem';

# chains

Get the complete options chain for a ticker.

```python wordwrap
chains(symbol: Union[str, List[str]], provider: Literal[str] = intrinio)
```

---

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

---

## Returns

```python wordwrap
OBBject
    results : List[OptionsChains]
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

