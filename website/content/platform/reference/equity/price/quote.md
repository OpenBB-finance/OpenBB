---
title: "quote"
description: "Learn how to load stock data for a specific ticker with the Equity Quote  function. Discover the various parameters and data returned, including day low,  day high, date, symbol, name, price, volume, and more."
keywords:
- equity quote
- stock data
- ticker
- parameters
- symbol
- provider
- returns
- data
- day low
- day high
- date
- fmp
- intrinio
- source
- results
- warnings
- chart
- metadata
- price
- changes percentage
- change
- year high
- year low
- market cap
- price avg50
- price avg200
- volume
- avg volume
- exchange
- open
- previous close
- eps
- pe
- earnings announcement
- shares outstanding
- last price
- last time
- last size
- bid price
- bid size
- ask price
- ask size
- close price
- high price
- low price
- exchange volume
- market volume
- updated on
- listing venue
- sales conditions
- quote conditions
- market center code
- is darkpool
- messages
- security
---

import HeadTitle from '@site/src/components/General/HeadTitle.tsx';

<HeadTitle title="equity/price/quote - Reference | OpenBB Platform Docs" />

<!-- markdownlint-disable MD012 MD031 MD033 -->

import Tabs from '@theme/Tabs';
import TabItem from '@theme/TabItem';

Get the latest quote for a given stock. Quote includes price, volume, and other data.


Examples
--------

```python
from openbb import obb
obb.equity.price.quote(symbol='AAPL', provider='fmp')
```

---

## Parameters

<Tabs>

<TabItem value='standard' label='standard'>

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| symbol | Union[str, List[str]] | Symbol to get data for. This endpoint will accept multiple symbols separated by commas. Multiple items allowed for provider(s): cboe, fmp, intrinio, tmx, tradier, yfinance. |  | False |
| provider | Literal['cboe', 'fmp', 'intrinio', 'tmx', 'tradier', 'yfinance'] | The provider to use for the query, by default None. If None, the provider specified in defaults is selected or 'cboe' if there is no default. | cboe | True |
</TabItem>

<TabItem value='cboe' label='cboe'>

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| symbol | Union[str, List[str]] | Symbol to get data for. This endpoint will accept multiple symbols separated by commas. Multiple items allowed for provider(s): cboe, fmp, intrinio, tmx, tradier, yfinance. |  | False |
| provider | Literal['cboe', 'fmp', 'intrinio', 'tmx', 'tradier', 'yfinance'] | The provider to use for the query, by default None. If None, the provider specified in defaults is selected or 'cboe' if there is no default. | cboe | True |
| use_cache | bool | When True, the company directories will be cached for 24 hours and are used to validate symbols. The results of the function are not cached. Set as False to bypass. | True | True |
</TabItem>

<TabItem value='fmp' label='fmp'>

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| symbol | Union[str, List[str]] | Symbol to get data for. This endpoint will accept multiple symbols separated by commas. Multiple items allowed for provider(s): cboe, fmp, intrinio, tmx, tradier, yfinance. |  | False |
| provider | Literal['cboe', 'fmp', 'intrinio', 'tmx', 'tradier', 'yfinance'] | The provider to use for the query, by default None. If None, the provider specified in defaults is selected or 'cboe' if there is no default. | cboe | True |
</TabItem>

<TabItem value='intrinio' label='intrinio'>

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| symbol | Union[str, List[str]] | Symbol to get data for. This endpoint will accept multiple symbols separated by commas. Multiple items allowed for provider(s): cboe, fmp, intrinio, tmx, tradier, yfinance. |  | False |
| provider | Literal['cboe', 'fmp', 'intrinio', 'tmx', 'tradier', 'yfinance'] | The provider to use for the query, by default None. If None, the provider specified in defaults is selected or 'cboe' if there is no default. | cboe | True |
| source | Literal['iex', 'bats', 'bats_delayed', 'utp_delayed', 'cta_a_delayed', 'cta_b_delayed', 'intrinio_mx', 'intrinio_mx_plus', 'delayed_sip'] | Source of the data. | iex | True |
</TabItem>

<TabItem value='tmx' label='tmx'>

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| symbol | Union[str, List[str]] | Symbol to get data for. This endpoint will accept multiple symbols separated by commas. Multiple items allowed for provider(s): cboe, fmp, intrinio, tmx, tradier, yfinance. |  | False |
| provider | Literal['cboe', 'fmp', 'intrinio', 'tmx', 'tradier', 'yfinance'] | The provider to use for the query, by default None. If None, the provider specified in defaults is selected or 'cboe' if there is no default. | cboe | True |
</TabItem>

<TabItem value='tradier' label='tradier'>

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| symbol | Union[str, List[str]] | Symbol to get data for. This endpoint will accept multiple symbols separated by commas. Multiple items allowed for provider(s): cboe, fmp, intrinio, tmx, tradier, yfinance. |  | False |
| provider | Literal['cboe', 'fmp', 'intrinio', 'tmx', 'tradier', 'yfinance'] | The provider to use for the query, by default None. If None, the provider specified in defaults is selected or 'cboe' if there is no default. | cboe | True |
</TabItem>

<TabItem value='yfinance' label='yfinance'>

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| symbol | Union[str, List[str]] | Symbol to get data for. This endpoint will accept multiple symbols separated by commas. Multiple items allowed for provider(s): cboe, fmp, intrinio, tmx, tradier, yfinance. |  | False |
| provider | Literal['cboe', 'fmp', 'intrinio', 'tmx', 'tradier', 'yfinance'] | The provider to use for the query, by default None. If None, the provider specified in defaults is selected or 'cboe' if there is no default. | cboe | True |
</TabItem>

</Tabs>

---

## Returns

```python wordwrap
OBBject
    results : EquityQuote
        Serializable results.
    provider : Literal['cboe', 'fmp', 'intrinio', 'tmx', 'tradier', 'yfinance']
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
| asset_type | str | Type of asset - i.e, stock, ETF, etc. |
| name | str | Name of the company or asset. |
| exchange | str | The name or symbol of the venue where the data is from. |
| bid | float | Price of the top bid order. |
| bid_size | int | This represents the number of round lot orders at the given price. The normal round lot size is 100 shares. A size of 2 means there are 200 shares available at the given price. |
| bid_exchange | str | The specific trading venue where the purchase order was placed. |
| ask | float | Price of the top ask order. |
| ask_size | int | This represents the number of round lot orders at the given price. The normal round lot size is 100 shares. A size of 2 means there are 200 shares available at the given price. |
| ask_exchange | str | The specific trading venue where the sale order was placed. |
| quote_conditions | Union[str, int, List[str], List[int]] | Conditions or condition codes applicable to the quote. |
| quote_indicators | Union[str, int, List[str], List[int]] | Indicators or indicator codes applicable to the participant quote related to the price bands for the issue, or the affect the quote has on the NBBO. |
| sales_conditions | Union[str, int, List[str], List[int]] | Conditions or condition codes applicable to the sale. |
| sequence_number | int | The sequence number represents the sequence in which message events happened. These are increasing and unique per ticker symbol, but will not always be sequential (e.g., 1, 2, 6, 9, 10, 11). |
| market_center | str | The ID of the UTP participant that originated the message. |
| participant_timestamp | datetime | Timestamp for when the quote was generated by the exchange. |
| trf_timestamp | datetime | Timestamp for when the TRF (Trade Reporting Facility) received the message. |
| sip_timestamp | datetime | Timestamp for when the SIP (Security Information Processor) received the message from the exchange. |
| last_price | float | Price of the last trade. |
| last_tick | str | Whether the last sale was an up or down tick. |
| last_size | int | Size of the last trade. |
| last_timestamp | datetime | Date and Time when the last price was recorded. |
| open | float | The open price. |
| high | float | The high price. |
| low | float | The low price. |
| close | float | The close price. |
| volume | Union[int, float] | The trading volume. |
| exchange_volume | Union[int, float] | Volume of shares exchanged during the trading day on the specific exchange. |
| prev_close | float | The previous close price. |
| change | float | Change in price from previous close. |
| change_percent | float | Change in price as a normalized percentage. |
| year_high | float | The one year high (52W High). |
| year_low | float | The one year low (52W Low). |
</TabItem>

<TabItem value='cboe' label='cboe'>

| Name | Type | Description |
| ---- | ---- | ----------- |
| symbol | str | Symbol representing the entity requested in the data. |
| asset_type | str | Type of asset - i.e, stock, ETF, etc. |
| name | str | Name of the company or asset. |
| exchange | str | The name or symbol of the venue where the data is from. |
| bid | float | Price of the top bid order. |
| bid_size | int | This represents the number of round lot orders at the given price. The normal round lot size is 100 shares. A size of 2 means there are 200 shares available at the given price. |
| bid_exchange | str | The specific trading venue where the purchase order was placed. |
| ask | float | Price of the top ask order. |
| ask_size | int | This represents the number of round lot orders at the given price. The normal round lot size is 100 shares. A size of 2 means there are 200 shares available at the given price. |
| ask_exchange | str | The specific trading venue where the sale order was placed. |
| quote_conditions | Union[str, int, List[str], List[int]] | Conditions or condition codes applicable to the quote. |
| quote_indicators | Union[str, int, List[str], List[int]] | Indicators or indicator codes applicable to the participant quote related to the price bands for the issue, or the affect the quote has on the NBBO. |
| sales_conditions | Union[str, int, List[str], List[int]] | Conditions or condition codes applicable to the sale. |
| sequence_number | int | The sequence number represents the sequence in which message events happened. These are increasing and unique per ticker symbol, but will not always be sequential (e.g., 1, 2, 6, 9, 10, 11). |
| market_center | str | The ID of the UTP participant that originated the message. |
| participant_timestamp | datetime | Timestamp for when the quote was generated by the exchange. |
| trf_timestamp | datetime | Timestamp for when the TRF (Trade Reporting Facility) received the message. |
| sip_timestamp | datetime | Timestamp for when the SIP (Security Information Processor) received the message from the exchange. |
| last_price | float | Price of the last trade. |
| last_tick | str | Whether the last sale was an up or down tick. |
| last_size | int | Size of the last trade. |
| last_timestamp | datetime | Date and Time when the last price was recorded. |
| open | float | The open price. |
| high | float | The high price. |
| low | float | The low price. |
| close | float | The close price. |
| volume | Union[int, float] | The trading volume. |
| exchange_volume | Union[int, float] | Volume of shares exchanged during the trading day on the specific exchange. |
| prev_close | float | The previous close price. |
| change | float | Change in price from previous close. |
| change_percent | float | Change in price as a normalized percentage. |
| year_high | float | The one year high (52W High). |
| year_low | float | The one year low (52W Low). |
| iv30 | float | The 30-day implied volatility of the stock. |
| iv30_change | float | Change in 30-day implied volatility of the stock. |
| iv30_change_percent | float | Change in 30-day implied volatility of the stock as a normalized percentage value. |
| iv30_annual_high | float | The 1-year high of 30-day implied volatility. |
| hv30_annual_high | float | The 1-year high of 30-day realized volatility. |
| iv30_annual_low | float | The 1-year low of 30-day implied volatility. |
| hv30_annual_low | float | The 1-year low of 30-dayrealized volatility. |
| iv60_annual_high | float | The 1-year high of 60-day implied volatility. |
| hv60_annual_high | float | The 1-year high of 60-day realized volatility. |
| iv60_annual_low | float | The 1-year low of 60-day implied volatility. |
| hv60_annual_low | float | The 1-year low of 60-day realized volatility. |
| iv90_annual_high | float | The 1-year high of 90-day implied volatility. |
| hv90_annual_high | float | The 1-year high of 90-day realized volatility. |
| iv90_annual_low | float | The 1-year low of 90-day implied volatility. |
| hv90_annual_low | float | The 1-year low of 90-day realized volatility. |
</TabItem>

<TabItem value='fmp' label='fmp'>

| Name | Type | Description |
| ---- | ---- | ----------- |
| symbol | str | Symbol representing the entity requested in the data. |
| asset_type | str | Type of asset - i.e, stock, ETF, etc. |
| name | str | Name of the company or asset. |
| exchange | str | The name or symbol of the venue where the data is from. |
| bid | float | Price of the top bid order. |
| bid_size | int | This represents the number of round lot orders at the given price. The normal round lot size is 100 shares. A size of 2 means there are 200 shares available at the given price. |
| bid_exchange | str | The specific trading venue where the purchase order was placed. |
| ask | float | Price of the top ask order. |
| ask_size | int | This represents the number of round lot orders at the given price. The normal round lot size is 100 shares. A size of 2 means there are 200 shares available at the given price. |
| ask_exchange | str | The specific trading venue where the sale order was placed. |
| quote_conditions | Union[str, int, List[str], List[int]] | Conditions or condition codes applicable to the quote. |
| quote_indicators | Union[str, int, List[str], List[int]] | Indicators or indicator codes applicable to the participant quote related to the price bands for the issue, or the affect the quote has on the NBBO. |
| sales_conditions | Union[str, int, List[str], List[int]] | Conditions or condition codes applicable to the sale. |
| sequence_number | int | The sequence number represents the sequence in which message events happened. These are increasing and unique per ticker symbol, but will not always be sequential (e.g., 1, 2, 6, 9, 10, 11). |
| market_center | str | The ID of the UTP participant that originated the message. |
| participant_timestamp | datetime | Timestamp for when the quote was generated by the exchange. |
| trf_timestamp | datetime | Timestamp for when the TRF (Trade Reporting Facility) received the message. |
| sip_timestamp | datetime | Timestamp for when the SIP (Security Information Processor) received the message from the exchange. |
| last_price | float | Price of the last trade. |
| last_tick | str | Whether the last sale was an up or down tick. |
| last_size | int | Size of the last trade. |
| last_timestamp | datetime | Date and Time when the last price was recorded. |
| open | float | The open price. |
| high | float | The high price. |
| low | float | The low price. |
| close | float | The close price. |
| volume | Union[int, float] | The trading volume. |
| exchange_volume | Union[int, float] | Volume of shares exchanged during the trading day on the specific exchange. |
| prev_close | float | The previous close price. |
| change | float | Change in price from previous close. |
| change_percent | float | Change in price as a normalized percentage. |
| year_high | float | The one year high (52W High). |
| year_low | float | The one year low (52W Low). |
| price_avg50 | float | 50 day moving average price. |
| price_avg200 | float | 200 day moving average price. |
| avg_volume | int | Average volume over the last 10 trading days. |
| market_cap | float | Market cap of the company. |
| shares_outstanding | int | Number of shares outstanding. |
| eps | float | Earnings per share. |
| pe | float | Price earnings ratio. |
| earnings_announcement | Union[datetime, str] | Upcoming earnings announcement date. |
</TabItem>

<TabItem value='intrinio' label='intrinio'>

| Name | Type | Description |
| ---- | ---- | ----------- |
| symbol | str | Symbol representing the entity requested in the data. |
| asset_type | str | Type of asset - i.e, stock, ETF, etc. |
| name | str | Name of the company or asset. |
| exchange | str | The name or symbol of the venue where the data is from. |
| bid | float | Price of the top bid order. |
| bid_size | int | This represents the number of round lot orders at the given price. The normal round lot size is 100 shares. A size of 2 means there are 200 shares available at the given price. |
| bid_exchange | str | The specific trading venue where the purchase order was placed. |
| ask | float | Price of the top ask order. |
| ask_size | int | This represents the number of round lot orders at the given price. The normal round lot size is 100 shares. A size of 2 means there are 200 shares available at the given price. |
| ask_exchange | str | The specific trading venue where the sale order was placed. |
| quote_conditions | Union[str, int, List[str], List[int]] | Conditions or condition codes applicable to the quote. |
| quote_indicators | Union[str, int, List[str], List[int]] | Indicators or indicator codes applicable to the participant quote related to the price bands for the issue, or the affect the quote has on the NBBO. |
| sales_conditions | Union[str, int, List[str], List[int]] | Conditions or condition codes applicable to the sale. |
| sequence_number | int | The sequence number represents the sequence in which message events happened. These are increasing and unique per ticker symbol, but will not always be sequential (e.g., 1, 2, 6, 9, 10, 11). |
| market_center | str | The ID of the UTP participant that originated the message. |
| participant_timestamp | datetime | Timestamp for when the quote was generated by the exchange. |
| trf_timestamp | datetime | Timestamp for when the TRF (Trade Reporting Facility) received the message. |
| sip_timestamp | datetime | Timestamp for when the SIP (Security Information Processor) received the message from the exchange. |
| last_price | float | Price of the last trade. |
| last_tick | str | Whether the last sale was an up or down tick. |
| last_size | int | Size of the last trade. |
| last_timestamp | datetime | Date and Time when the last price was recorded. |
| open | float | The open price. |
| high | float | The high price. |
| low | float | The low price. |
| close | float | The close price. |
| volume | Union[int, float] | The trading volume. |
| exchange_volume | Union[int, float] | Volume of shares exchanged during the trading day on the specific exchange. |
| prev_close | float | The previous close price. |
| change | float | Change in price from previous close. |
| change_percent | float | Change in price as a normalized percentage. |
| year_high | float | The one year high (52W High). |
| year_low | float | The one year low (52W Low). |
| is_darkpool | bool | Whether or not the current trade is from a darkpool. |
| source | str | Source of the Intrinio data. |
| updated_on | datetime | Date and Time when the data was last updated. |
| security | openbb_intrinio.utils.references.IntrinioSecurity | Security details related to the quote. |
</TabItem>

<TabItem value='tmx' label='tmx'>

| Name | Type | Description |
| ---- | ---- | ----------- |
| symbol | str | Symbol representing the entity requested in the data. |
| asset_type | str | Type of asset - i.e, stock, ETF, etc. |
| name | str | Name of the company or asset. |
| exchange | str | The name or symbol of the venue where the data is from. |
| bid | float | Price of the top bid order. |
| bid_size | int | This represents the number of round lot orders at the given price. The normal round lot size is 100 shares. A size of 2 means there are 200 shares available at the given price. |
| bid_exchange | str | The specific trading venue where the purchase order was placed. |
| ask | float | Price of the top ask order. |
| ask_size | int | This represents the number of round lot orders at the given price. The normal round lot size is 100 shares. A size of 2 means there are 200 shares available at the given price. |
| ask_exchange | str | The specific trading venue where the sale order was placed. |
| quote_conditions | Union[str, int, List[str], List[int]] | Conditions or condition codes applicable to the quote. |
| quote_indicators | Union[str, int, List[str], List[int]] | Indicators or indicator codes applicable to the participant quote related to the price bands for the issue, or the affect the quote has on the NBBO. |
| sales_conditions | Union[str, int, List[str], List[int]] | Conditions or condition codes applicable to the sale. |
| sequence_number | int | The sequence number represents the sequence in which message events happened. These are increasing and unique per ticker symbol, but will not always be sequential (e.g., 1, 2, 6, 9, 10, 11). |
| market_center | str | The ID of the UTP participant that originated the message. |
| participant_timestamp | datetime | Timestamp for when the quote was generated by the exchange. |
| trf_timestamp | datetime | Timestamp for when the TRF (Trade Reporting Facility) received the message. |
| sip_timestamp | datetime | Timestamp for when the SIP (Security Information Processor) received the message from the exchange. |
| last_price | float | Price of the last trade. |
| last_tick | str | Whether the last sale was an up or down tick. |
| last_size | int | Size of the last trade. |
| last_timestamp | datetime | Date and Time when the last price was recorded. |
| open | float | The open price. |
| high | float | The high price. |
| low | float | The low price. |
| close | float | The close price. |
| volume | Union[int, float] | The trading volume. |
| exchange_volume | Union[int, float] | Volume of shares exchanged during the trading day on the specific exchange. |
| prev_close | float | The previous close price. |
| change | float | Change in price from previous close. |
| change_percent | float | Change in price as a normalized percentage. |
| year_high | float | The one year high (52W High). |
| year_low | float | The one year low (52W Low). |
| security_type | str | The issuance type of the asset. |
| sector | str | The sector of the asset. |
| industry_category | str | The industry category of the asset. |
| industry_group | str | The industry group of the asset. |
| vwap | float | Volume Weighted Average Price over the period. |
| ma_21 | float | Twenty-one day moving average. |
| ma_50 | float | Fifty day moving average. |
| ma_200 | float | Two-hundred day moving average. |
| volume_avg_10d | int | Ten day average volume. |
| volume_avg_30d | int | Thirty day average volume. |
| volume_avg_50d | int | Fifty day average volume. |
| market_cap | int | Market capitalization. |
| market_cap_all_classes | int | Market capitalization of all share classes. |
| div_amount | float | The most recent dividend amount. |
| div_currency | str | The currency the dividend is paid in. |
| div_yield | float | The dividend yield as a normalized percentage. |
| div_freq | str | The frequency of dividend payments. |
| div_ex_date | date | The ex-dividend date. |
| div_pay_date | date | The next dividend ayment date. |
| div_growth_3y | Union[str, float] | The three year dividend growth as a normalized percentage. |
| div_growth_5y | Union[str, float] | The five year dividend growth as a normalized percentage. |
| pe | Union[str, float] | The price to earnings ratio. |
| eps | Union[str, float] | The earnings per share. |
| debt_to_equity | Union[str, float] | The debt to equity ratio. |
| price_to_book | Union[str, float] | The price to book ratio. |
| price_to_cf | Union[str, float] | The price to cash flow ratio. |
| return_on_equity | Union[str, float] | The return on equity, as a normalized percentage. |
| return_on_assets | Union[str, float] | The return on assets, as a normalized percentage. |
| beta | Union[str, float] | The beta relative to the TSX Composite. |
| alpha | Union[str, float] | The alpha relative to the TSX Composite. |
| shares_outstanding | int | The number of listed shares outstanding. |
| shares_escrow | int | The number of shares held in escrow. |
| shares_total | int | The total number of shares outstanding from all classes. |
</TabItem>

<TabItem value='tradier' label='tradier'>

| Name | Type | Description |
| ---- | ---- | ----------- |
| symbol | str | Symbol representing the entity requested in the data. |
| asset_type | str | Type of asset - i.e, stock, ETF, etc. |
| name | str | Name of the company or asset. |
| exchange | str | The name or symbol of the venue where the data is from. |
| bid | float | Price of the top bid order. |
| bid_size | int | This represents the number of round lot orders at the given price. The normal round lot size is 100 shares. A size of 2 means there are 200 shares available at the given price. |
| bid_exchange | str | The specific trading venue where the purchase order was placed. |
| ask | float | Price of the top ask order. |
| ask_size | int | This represents the number of round lot orders at the given price. The normal round lot size is 100 shares. A size of 2 means there are 200 shares available at the given price. |
| ask_exchange | str | The specific trading venue where the sale order was placed. |
| quote_conditions | Union[str, int, List[str], List[int]] | Conditions or condition codes applicable to the quote. |
| quote_indicators | Union[str, int, List[str], List[int]] | Indicators or indicator codes applicable to the participant quote related to the price bands for the issue, or the affect the quote has on the NBBO. |
| sales_conditions | Union[str, int, List[str], List[int]] | Conditions or condition codes applicable to the sale. |
| sequence_number | int | The sequence number represents the sequence in which message events happened. These are increasing and unique per ticker symbol, but will not always be sequential (e.g., 1, 2, 6, 9, 10, 11). |
| market_center | str | The ID of the UTP participant that originated the message. |
| participant_timestamp | datetime | Timestamp for when the quote was generated by the exchange. |
| trf_timestamp | datetime | Timestamp for when the TRF (Trade Reporting Facility) received the message. |
| sip_timestamp | datetime | Timestamp for when the SIP (Security Information Processor) received the message from the exchange. |
| last_price | float | Price of the last trade. |
| last_tick | str | Whether the last sale was an up or down tick. |
| last_size | int | Size of the last trade. |
| last_timestamp | datetime | Date and Time when the last price was recorded. |
| open | float | The open price. |
| high | float | The high price. |
| low | float | The low price. |
| close | float | The close price. |
| volume | Union[int, float] | The trading volume. |
| exchange_volume | Union[int, float] | Volume of shares exchanged during the trading day on the specific exchange. |
| prev_close | float | The previous close price. |
| change | float | Change in price from previous close. |
| change_percent | float | Change in price as a normalized percentage. |
| year_high | float | The one year high (52W High). |
| year_low | float | The one year low (52W Low). |
| last_volume | int | The last trade volume. |
| volume_avg | int | The average daily trading volume. |
| bid_timestamp | datetime | Timestamp of the bid price. |
| ask_timestamp | datetime | Timestamp of the ask price. |
| greeks_timestamp | datetime | Timestamp of the greeks data. |
| underlying | str | The underlying symbol for the option. |
| root_symbol | str | The root symbol for the option. |
| option_type | Literal['call', 'put'] | Type of option - call or put. |
| contract_size | int | The number of shares in a standard contract. |
| expiration_type | str | The expiration type of the option - i.e, standard, weekly, etc. |
| expiration_date | date | The expiration date of the option. |
| strike | float | The strike price of the option. |
| open_interest | int | The number of open contracts for the option. |
| bid_iv | float | Implied volatility of the bid price. |
| ask_iv | float | Implied volatility of the ask price. |
| mid_iv | float | Mid-point implied volatility of the option. |
| orats_final_iv | float | ORATS final implied volatility of the option. |
| delta | float | Delta of the option. |
| gamma | float | Gamma of the option. |
| theta | float | Theta of the option. |
| vega | float | Vega of the option. |
| rho | float | Rho of the option. |
| phi | float | Phi of the option. |
</TabItem>

<TabItem value='yfinance' label='yfinance'>

| Name | Type | Description |
| ---- | ---- | ----------- |
| symbol | str | Symbol representing the entity requested in the data. |
| asset_type | str | Type of asset - i.e, stock, ETF, etc. |
| name | str | Name of the company or asset. |
| exchange | str | The name or symbol of the venue where the data is from. |
| bid | float | Price of the top bid order. |
| bid_size | int | This represents the number of round lot orders at the given price. The normal round lot size is 100 shares. A size of 2 means there are 200 shares available at the given price. |
| bid_exchange | str | The specific trading venue where the purchase order was placed. |
| ask | float | Price of the top ask order. |
| ask_size | int | This represents the number of round lot orders at the given price. The normal round lot size is 100 shares. A size of 2 means there are 200 shares available at the given price. |
| ask_exchange | str | The specific trading venue where the sale order was placed. |
| quote_conditions | Union[str, int, List[str], List[int]] | Conditions or condition codes applicable to the quote. |
| quote_indicators | Union[str, int, List[str], List[int]] | Indicators or indicator codes applicable to the participant quote related to the price bands for the issue, or the affect the quote has on the NBBO. |
| sales_conditions | Union[str, int, List[str], List[int]] | Conditions or condition codes applicable to the sale. |
| sequence_number | int | The sequence number represents the sequence in which message events happened. These are increasing and unique per ticker symbol, but will not always be sequential (e.g., 1, 2, 6, 9, 10, 11). |
| market_center | str | The ID of the UTP participant that originated the message. |
| participant_timestamp | datetime | Timestamp for when the quote was generated by the exchange. |
| trf_timestamp | datetime | Timestamp for when the TRF (Trade Reporting Facility) received the message. |
| sip_timestamp | datetime | Timestamp for when the SIP (Security Information Processor) received the message from the exchange. |
| last_price | float | Price of the last trade. |
| last_tick | str | Whether the last sale was an up or down tick. |
| last_size | int | Size of the last trade. |
| last_timestamp | datetime | Date and Time when the last price was recorded. |
| open | float | The open price. |
| high | float | The high price. |
| low | float | The low price. |
| close | float | The close price. |
| volume | Union[int, float] | The trading volume. |
| exchange_volume | Union[int, float] | Volume of shares exchanged during the trading day on the specific exchange. |
| prev_close | float | The previous close price. |
| change | float | Change in price from previous close. |
| change_percent | float | Change in price as a normalized percentage. |
| year_high | float | The one year high (52W High). |
| year_low | float | The one year low (52W Low). |
| ma_50d | float | 50-day moving average price. |
| ma_200d | float | 200-day moving average price. |
| volume_average | float | Average daily trading volume. |
| volume_average_10d | float | Average daily trading volume in the last 10 days. |
| currency | str | Currency of the price. |
</TabItem>

</Tabs>

