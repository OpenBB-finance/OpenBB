---
title: OptionsChains
description: OpenBB Platform Data Model
---


import Tabs from '@theme/Tabs';
import TabItem from '@theme/TabItem';


---

## Parameters

<Tabs>
<TabItem value="standard" label="Standard">

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| symbol | Union[str, List[str]] | Symbol to get data for. |  | False |
| provider | Union[Literal['cboe', 'intrinio']] | The provider to use for the query, by default None. If None, the provider specified in defaults is selected or 'cboe' if there is no default. | cboe | True |
</TabItem>

<TabItem value='intrinio' label='intrinio'>

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| symbol | Union[str, List[str]] | Symbol to get data for. |  | False |
| provider | Union[Literal['cboe', 'intrinio']] | The provider to use for the query, by default None. If None, the provider specified in defaults is selected or 'cboe' if there is no default. | cboe | True |
| date | Union[str] | Date for which the options chains are returned. |  | False |
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
| close | Union[float] | Close price for the option that day. |
| close_bid | Union[float] | The closing bid price for the option that day. |
| close_ask | Union[float] | The closing ask price for the option that day. |
| volume | Union[float] | Current trading volume on the contract. |
| open | Union[float] | Opening price of the option. |
| open_bid | Union[float] | The opening bid price for the option that day. |
| open_ask | Union[float] | The opening ask price for the option that day. |
| open_interest | Union[float] | Open interest on the contract. |
| high | Union[float] | High price of the option. |
| low | Union[float] | Low price of the option. |
| mark | Union[float] | The mid-price between the latest bid-ask spread. |
| ask_high | Union[float] | The highest ask price for the option that day. |
| ask_low | Union[float] | The lowest ask price for the option that day. |
| bid_high | Union[float] | The highest bid price for the option that day. |
| bid_low | Union[float] | The lowest bid price for the option that day. |
| implied_volatility | Union[float] | Implied volatility of the option. |
| delta | Union[float] | Delta of the option. |
| gamma | Union[float] | Gamma of the option. |
| theta | Union[float] | Theta of the option. |
| vega | Union[float] | Vega of the option. |
</TabItem>

<TabItem value='cboe' label='cboe'>

| Name | Type | Description |
| ---- | ---- | ----------- |
| contract_symbol | str | Contract symbol for the option. |
| symbol | str | Underlying symbol for the option. |
| expiration | date | Expiration date of the contract. |
| strike | float | Strike price of the contract. |
| type | str | Call or Put. |
| date | date | Date for which the options chains are returned. |
| close | Union[float] | Close price for the option that day. |
| close_bid | Union[float] | The closing bid price for the option that day. |
| close_ask | Union[float] | The closing ask price for the option that day. |
| volume | Union[float] | Current trading volume on the contract. |
| open | Union[float] | Opening price of the option. |
| open_bid | Union[float] | The opening bid price for the option that day. |
| open_ask | Union[float] | The opening ask price for the option that day. |
| open_interest | Union[float] | Open interest on the contract. |
| high | Union[float] | High price of the option. |
| low | Union[float] | Low price of the option. |
| mark | Union[float] | The mid-price between the latest bid-ask spread. |
| ask_high | Union[float] | The highest ask price for the option that day. |
| ask_low | Union[float] | The lowest ask price for the option that day. |
| bid_high | Union[float] | The highest bid price for the option that day. |
| bid_low | Union[float] | The lowest bid price for the option that day. |
| implied_volatility | Union[float] | Implied volatility of the option. |
| delta | Union[float] | Delta of the option. |
| gamma | Union[float] | Gamma of the option. |
| theta | Union[float] | Theta of the option. |
| vega | Union[float] | Vega of the option. |
| bid_size | int | Bid size for the option. |
| ask_size | int | Ask size for the option. |
| theoretical | float | Theoretical value of the option. |
| last_trade_price | float | Last trade price of the option. |
| tick | str | Whether the last tick was up or down in price. |
| prev_close | float | Previous closing price of the option. |
| change | float | Change in  price of the option. |
| change_percent | float | Change, in percent, of the option. |
| rho | float | Rho of the option. |
| last_trade_timestamp | datetime | Last trade timestamp of the option. |
| dte | int | Days to expiration for the option. |
</TabItem>

</Tabs>

