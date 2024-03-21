---
title: "chains"
description: "Learn how to get the complete options chain for a ticker using the OBB.equity.options.chains  function. Explore the available parameters like symbol and provider, and understand  the data returned, including contract symbol, expiration, strike price, and more."
keywords:
- options chain
- ticker
- complete options chain
- symbol
- provider
- data
- contract symbol
- expiration
- strike price
- option type
- eod date
- trading volume
- open price
- open interest
- high price
- low price
- implied volatility
- delta
- gamma
- theta
- vega
- bid size
- ask size
- theoretical value
- last trade price
- prev close
- change percent
- rho
- last trade timestamp
- dte
---

import HeadTitle from '@site/src/components/General/HeadTitle.tsx';

<HeadTitle title="derivatives/options/chains - Reference | OpenBB Platform Docs" />

<!-- markdownlint-disable MD012 MD031 MD033 -->

import Tabs from '@theme/Tabs';
import TabItem from '@theme/TabItem';

Get the complete options chain for a ticker.


Examples
--------

```python
from openbb import obb
obb.derivatives.options.chains(symbol='AAPL', provider='intrinio')
# Use the "date" parameter to get the end-of-day-data for a specific date, where supported.
obb.derivatives.options.chains(symbol='AAPL', date=2023-01-25, provider='intrinio')
```

---

## Parameters

<Tabs>

<TabItem value='standard' label='standard'>

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| symbol | str | Symbol to get data for. |  | False |
| provider | Literal['cboe', 'intrinio', 'tmx', 'tradier'] | The provider to use for the query, by default None. If None, the provider specified in defaults is selected or 'cboe' if there is no default. | cboe | True |
</TabItem>

<TabItem value='cboe' label='cboe'>

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| symbol | str | Symbol to get data for. |  | False |
| provider | Literal['cboe', 'intrinio', 'tmx', 'tradier'] | The provider to use for the query, by default None. If None, the provider specified in defaults is selected or 'cboe' if there is no default. | cboe | True |
| use_cache | bool | When True, the company directories will be cached for24 hours and are used to validate symbols. The results of the function are not cached. Set as False to bypass. | True | True |
</TabItem>

<TabItem value='intrinio' label='intrinio'>

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| symbol | str | Symbol to get data for. |  | False |
| provider | Literal['cboe', 'intrinio', 'tmx', 'tradier'] | The provider to use for the query, by default None. If None, the provider specified in defaults is selected or 'cboe' if there is no default. | cboe | True |
| date | Union[date, str] | The end-of-day date for options chains data. | None | True |
</TabItem>

<TabItem value='tmx' label='tmx'>

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| symbol | str | Symbol to get data for. |  | False |
| provider | Literal['cboe', 'intrinio', 'tmx', 'tradier'] | The provider to use for the query, by default None. If None, the provider specified in defaults is selected or 'cboe' if there is no default. | cboe | True |
| date | Union[date, str] | A specific date to get data for. | None | True |
| use_cache | bool | Caching is used to validate the supplied ticker symbol, or if a historical EOD chain is requested. To bypass, set to False. | True | True |
</TabItem>

<TabItem value='tradier' label='tradier'>

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| symbol | str | Symbol to get data for. |  | False |
| provider | Literal['cboe', 'intrinio', 'tmx', 'tradier'] | The provider to use for the query, by default None. If None, the provider specified in defaults is selected or 'cboe' if there is no default. | cboe | True |
</TabItem>

</Tabs>

---

## Returns

```python wordwrap
OBBject
    results : OptionsChains
        Serializable results.
    provider : Literal['cboe', 'intrinio', 'tmx', 'tradier']
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
| symbol | str | Symbol representing the entity requested in the data. Here, it is the underlying symbol for the option. |
| contract_symbol | str | Contract symbol for the option. |
| eod_date | date | Date for which the options chains are returned. |
| expiration | date | Expiration date of the contract. |
| strike | float | Strike price of the contract. |
| option_type | str | Call or Put. |
| open_interest | int | Open interest on the contract. |
| volume | int | The trading volume. |
| theoretical_price | float | Theoretical value of the option. |
| last_trade_price | float | Last trade price of the option. |
| tick | str | Whether the last tick was up or down in price. |
| bid | float | Current bid price for the option. |
| bid_size | int | Bid size for the option. |
| ask | float | Current ask price for the option. |
| ask_size | int | Ask size for the option. |
| mark | float | The mid-price between the latest bid and ask. |
| open | float | The open price. |
| open_bid | float | The opening bid price for the option that day. |
| open_ask | float | The opening ask price for the option that day. |
| high | float | The high price. |
| bid_high | float | The highest bid price for the option that day. |
| ask_high | float | The highest ask price for the option that day. |
| low | float | The low price. |
| bid_low | float | The lowest bid price for the option that day. |
| ask_low | float | The lowest ask price for the option that day. |
| close | float | The close price. |
| close_size | int | The closing trade size for the option that day. |
| close_time | datetime | The time of the closing price for the option that day. |
| close_bid | float | The closing bid price for the option that day. |
| close_bid_size | int | The closing bid size for the option that day. |
| close_bid_time | datetime | The time of the bid closing price for the option that day. |
| close_ask | float | The closing ask price for the option that day. |
| close_ask_size | int | The closing ask size for the option that day. |
| close_ask_time | datetime | The time of the ask closing price for the option that day. |
| prev_close | float | The previous close price. |
| change | float | The change in the price of the option. |
| change_percent | float | Change, in normalizezd percentage points, of the option. |
| implied_volatility | float | Implied volatility of the option. |
| delta | float | Delta of the option. |
| gamma | float | Gamma of the option. |
| theta | float | Theta of the option. |
| vega | float | Vega of the option. |
| rho | float | Rho of the option. |
</TabItem>

<TabItem value='cboe' label='cboe'>

| Name | Type | Description |
| ---- | ---- | ----------- |
| symbol | str | Symbol representing the entity requested in the data. Here, it is the underlying symbol for the option. |
| contract_symbol | str | Contract symbol for the option. |
| eod_date | date | Date for which the options chains are returned. |
| expiration | date | Expiration date of the contract. |
| strike | float | Strike price of the contract. |
| option_type | str | Call or Put. |
| open_interest | int | Open interest on the contract. |
| volume | int | The trading volume. |
| theoretical_price | float | Theoretical value of the option. |
| last_trade_price | float | Last trade price of the option. |
| tick | str | Whether the last tick was up or down in price. |
| bid | float | Current bid price for the option. |
| bid_size | int | Bid size for the option. |
| ask | float | Current ask price for the option. |
| ask_size | int | Ask size for the option. |
| mark | float | The mid-price between the latest bid and ask. |
| open | float | The open price. |
| open_bid | float | The opening bid price for the option that day. |
| open_ask | float | The opening ask price for the option that day. |
| high | float | The high price. |
| bid_high | float | The highest bid price for the option that day. |
| ask_high | float | The highest ask price for the option that day. |
| low | float | The low price. |
| bid_low | float | The lowest bid price for the option that day. |
| ask_low | float | The lowest ask price for the option that day. |
| close | float | The close price. |
| close_size | int | The closing trade size for the option that day. |
| close_time | datetime | The time of the closing price for the option that day. |
| close_bid | float | The closing bid price for the option that day. |
| close_bid_size | int | The closing bid size for the option that day. |
| close_bid_time | datetime | The time of the bid closing price for the option that day. |
| close_ask | float | The closing ask price for the option that day. |
| close_ask_size | int | The closing ask size for the option that day. |
| close_ask_time | datetime | The time of the ask closing price for the option that day. |
| prev_close | float | The previous close price. |
| change | float | The change in the price of the option. |
| change_percent | float | Change, in normalizezd percentage points, of the option. |
| implied_volatility | float | Implied volatility of the option. |
| delta | float | Delta of the option. |
| gamma | float | Gamma of the option. |
| theta | float | Theta of the option. |
| vega | float | Vega of the option. |
| rho | float | Rho of the option. |
| last_trade_timestamp | datetime | Last trade timestamp of the option. |
| dte | int | Days to expiration for the option. |
</TabItem>

<TabItem value='intrinio' label='intrinio'>

| Name | Type | Description |
| ---- | ---- | ----------- |
| symbol | str | Symbol representing the entity requested in the data. Here, it is the underlying symbol for the option. |
| contract_symbol | str | Contract symbol for the option. |
| eod_date | date | Date for which the options chains are returned. |
| expiration | date | Expiration date of the contract. |
| strike | float | Strike price of the contract. |
| option_type | str | Call or Put. |
| open_interest | int | Open interest on the contract. |
| volume | int | The trading volume. |
| theoretical_price | float | Theoretical value of the option. |
| last_trade_price | float | Last trade price of the option. |
| tick | str | Whether the last tick was up or down in price. |
| bid | float | Current bid price for the option. |
| bid_size | int | Bid size for the option. |
| ask | float | Current ask price for the option. |
| ask_size | int | Ask size for the option. |
| mark | float | The mid-price between the latest bid and ask. |
| open | float | The open price. |
| open_bid | float | The opening bid price for the option that day. |
| open_ask | float | The opening ask price for the option that day. |
| high | float | The high price. |
| bid_high | float | The highest bid price for the option that day. |
| ask_high | float | The highest ask price for the option that day. |
| low | float | The low price. |
| bid_low | float | The lowest bid price for the option that day. |
| ask_low | float | The lowest ask price for the option that day. |
| close | float | The close price. |
| close_size | int | The closing trade size for the option that day. |
| close_time | datetime | The time of the closing price for the option that day. |
| close_bid | float | The closing bid price for the option that day. |
| close_bid_size | int | The closing bid size for the option that day. |
| close_bid_time | datetime | The time of the bid closing price for the option that day. |
| close_ask | float | The closing ask price for the option that day. |
| close_ask_size | int | The closing ask size for the option that day. |
| close_ask_time | datetime | The time of the ask closing price for the option that day. |
| prev_close | float | The previous close price. |
| change | float | The change in the price of the option. |
| change_percent | float | Change, in normalizezd percentage points, of the option. |
| implied_volatility | float | Implied volatility of the option. |
| delta | float | Delta of the option. |
| gamma | float | Gamma of the option. |
| theta | float | Theta of the option. |
| vega | float | Vega of the option. |
| rho | float | Rho of the option. |
| exercise_style | str | The exercise style of the option, American or European. |
</TabItem>

<TabItem value='tmx' label='tmx'>

| Name | Type | Description |
| ---- | ---- | ----------- |
| symbol | str | Symbol representing the entity requested in the data. Here, it is the underlying symbol for the option. |
| contract_symbol | str | Contract symbol for the option. |
| eod_date | date | Date for which the options chains are returned. |
| expiration | date | Expiration date of the contract. |
| strike | float | Strike price of the contract. |
| option_type | str | Call or Put. |
| open_interest | int | Open interest on the contract. |
| volume | int | The trading volume. |
| theoretical_price | float | Theoretical value of the option. |
| last_trade_price | float | Last trade price of the option. |
| tick | str | Whether the last tick was up or down in price. |
| bid | float | Current bid price for the option. |
| bid_size | int | Bid size for the option. |
| ask | float | Current ask price for the option. |
| ask_size | int | Ask size for the option. |
| mark | float | The mid-price between the latest bid and ask. |
| open | float | The open price. |
| open_bid | float | The opening bid price for the option that day. |
| open_ask | float | The opening ask price for the option that day. |
| high | float | The high price. |
| bid_high | float | The highest bid price for the option that day. |
| ask_high | float | The highest ask price for the option that day. |
| low | float | The low price. |
| bid_low | float | The lowest bid price for the option that day. |
| ask_low | float | The lowest ask price for the option that day. |
| close | float | The close price. |
| close_size | int | The closing trade size for the option that day. |
| close_time | datetime | The time of the closing price for the option that day. |
| close_bid | float | The closing bid price for the option that day. |
| close_bid_size | int | The closing bid size for the option that day. |
| close_bid_time | datetime | The time of the bid closing price for the option that day. |
| close_ask | float | The closing ask price for the option that day. |
| close_ask_size | int | The closing ask size for the option that day. |
| close_ask_time | datetime | The time of the ask closing price for the option that day. |
| prev_close | float | The previous close price. |
| change | float | The change in the price of the option. |
| change_percent | float | Change, in normalizezd percentage points, of the option. |
| implied_volatility | float | Implied volatility of the option. |
| delta | float | Delta of the option. |
| gamma | float | Gamma of the option. |
| theta | float | Theta of the option. |
| vega | float | Vega of the option. |
| rho | float | Rho of the option. |
| transactions | int | Number of transactions for the contract. |
| total_value | float | Total value of the transactions. |
| settlement_price | float | Settlement price on that date. |
| underlying_price | float | Price of the underlying stock on that date. |
| dte | int | Days to expiration for the option. |
</TabItem>

<TabItem value='tradier' label='tradier'>

| Name | Type | Description |
| ---- | ---- | ----------- |
| symbol | str | Symbol representing the entity requested in the data. Here, it is the underlying symbol for the option. |
| contract_symbol | str | Contract symbol for the option. |
| eod_date | date | Date for which the options chains are returned. |
| expiration | date | Expiration date of the contract. |
| strike | float | Strike price of the contract. |
| option_type | str | Call or Put. |
| open_interest | int | Open interest on the contract. |
| volume | int | The trading volume. |
| theoretical_price | float | Theoretical value of the option. |
| last_trade_price | float | Last trade price of the option. |
| tick | str | Whether the last tick was up or down in price. |
| bid | float | Current bid price for the option. |
| bid_size | int | Bid size for the option. |
| ask | float | Current ask price for the option. |
| ask_size | int | Ask size for the option. |
| mark | float | The mid-price between the latest bid and ask. |
| open | float | The open price. |
| open_bid | float | The opening bid price for the option that day. |
| open_ask | float | The opening ask price for the option that day. |
| high | float | The high price. |
| bid_high | float | The highest bid price for the option that day. |
| ask_high | float | The highest ask price for the option that day. |
| low | float | The low price. |
| bid_low | float | The lowest bid price for the option that day. |
| ask_low | float | The lowest ask price for the option that day. |
| close | float | The close price. |
| close_size | int | The closing trade size for the option that day. |
| close_time | datetime | The time of the closing price for the option that day. |
| close_bid | float | The closing bid price for the option that day. |
| close_bid_size | int | The closing bid size for the option that day. |
| close_bid_time | datetime | The time of the bid closing price for the option that day. |
| close_ask | float | The closing ask price for the option that day. |
| close_ask_size | int | The closing ask size for the option that day. |
| close_ask_time | datetime | The time of the ask closing price for the option that day. |
| prev_close | float | The previous close price. |
| change | float | The change in the price of the option. |
| change_percent | float | Change, in normalizezd percentage points, of the option. |
| implied_volatility | float | Implied volatility of the option. |
| delta | float | Delta of the option. |
| gamma | float | Gamma of the option. |
| theta | float | Theta of the option. |
| vega | float | Vega of the option. |
| rho | float | Rho of the option. |
| phi | float | Phi of the option. The sensitivity of the option relative to dividend yield. |
| bid_iv | float | Implied volatility of the bid price. |
| ask_iv | float | Implied volatility of the ask price. |
| orats_final_iv | float | ORATS final implied volatility of the option, updated once per hour. |
| year_high | float | 52-week high price of the option. |
| year_low | float | 52-week low price of the option. |
| last_trade_volume | int | Volume of the last trade. |
| dte | int | Days to expiration. |
| contract_size | int | Size of the contract. |
| bid_exchange | str | Exchange of the bid price. |
| bid_timestamp | datetime | Timestamp of the bid price. |
| ask_exchange | str | Exchange of the ask price. |
| ask_timestamp | datetime | Timestamp of the ask price. |
| greeks_timestamp | datetime | Timestamp of the last greeks update. Greeks/IV data is updated once per hour. |
| last_trade_timestamp | datetime | Timestamp of the last trade. |
</TabItem>

</Tabs>

