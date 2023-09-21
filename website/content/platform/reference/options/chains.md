---
title: chains
description: OpenBB Platform Function
---

import Tabs from '@theme/Tabs';
import TabItem from '@theme/TabItem';

# chains

Get the complete options chain for a ticker.

```python wordwrap
chains(symbol: Union[str, List[str]], provider: Literal[str] = cboe)
```

---

## Parameters

<Tabs>
<TabItem value="standard" label="Standard">

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| symbol | Union[str, List[str]] | Symbol to get data for. |  | False |
| provider | Literal['cboe'] | The provider to use for the query, by default None. If None, the provider specified in defaults is selected or 'cboe' if there is no default. | cboe | True |
</TabItem>

</Tabs>

---

## Returns

```python wordwrap
OBBject
    results : List[OptionsChains]
        Serializable results.

    provider : Optional[Literal['cboe']]
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
| expiration | datetime | Expiration date of the contract. |
| strike | float | Strike price of the contract. |
| option_type | str | Call or Put. |
| contract_symbol | str | Contract symbol for the option. |
| bid | float | Bid price of the contract. |
| ask | float | Ask price of the contract. |
| open_interest | float | Open interest on the contract. |
| volume | float | Current trading volume on the contract. |
</TabItem>

<TabItem value='cboe' label='cboe'>

| Name | Type | Description |
| ---- | ---- | ----------- |
| bid_size | int | Bid size for the option. |
| ask_size | int | Ask size for the option. |
| theoretical | float | Theoretical value of the option. |
| open | float | Opening price of the option. |
| high | float | High price of the option. |
| low | float | Low price of the option. |
| last_trade_price | float | Last trade price of the option. |
| tick | str | Whether the last tick was up or down in price. |
| prev_close | float | Previous closing price of the option. |
| change | float | Change in  price of the option. |
| change_percent | float | Change, in percent, of the option. |
| implied_volatility | float | Implied volatility of the option. |
| delta | float | Delta of the option. |
| gamma | float | Gamma of the option. |
| vega | float | Vega of the option. |
| theta | float | Theta of the option. |
| rho | float | Rho of the option. |
| last_trade_timestamp | datetime | Last trade timestamp of the option. |
| dte | int | Days to expiration for the option. |
</TabItem>

</Tabs>

