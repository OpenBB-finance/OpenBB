---
title: load
description: OpenBB Platform Function
---

import Tabs from '@theme/Tabs';
import TabItem from '@theme/TabItem';

# load

Load stock data for a specific ticker.

```python wordwrap
load(symbol: Union[str, List[str]], start_date: Union[date, str] = None, end_date: Union[date, str] = None, chart: bool = False, provider: Union[Literal[str]] = alpha_vantage)
```

---

## Parameters

<Tabs>
<TabItem value="standard" label="Standard">

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| symbol | Union[str, List[str]] | Symbol to get data for. |  | False |
| start_date | Union[date, str] | Start date of the data, in YYYY-MM-DD format. | None | True |
| end_date | Union[date, str] | End date of the data, in YYYY-MM-DD format. | None | True |
| chart | bool | Whether to create a chart or not, by default False. | False | True |
| provider | Union[Literal['alpha_vantage', 'cboe', 'fmp', 'intrinio', 'polygon', 'yfinance']] | The provider to use for the query, by default None. If None, the provider specified in defaults is selected or 'alpha_vantage' if there is no default. | alpha_vantage | True |
</TabItem>

<TabItem value='alpha_vantage' label='alpha_vantage'>

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| symbol | Union[str, List[str]] | Symbol to get data for. |  | False |
| start_date | Union[date, str] | Start date of the data, in YYYY-MM-DD format. | None | True |
| end_date | Union[date, str] | End date of the data, in YYYY-MM-DD format. | None | True |
| chart | bool | Whether to create a chart or not, by default False. | False | True |
| provider | Union[Literal['alpha_vantage', 'cboe', 'fmp', 'intrinio', 'polygon', 'yfinance']] | The provider to use for the query, by default None. If None, the provider specified in defaults is selected or 'alpha_vantage' if there is no default. | alpha_vantage | True |
| function_ | Literal['TIME_SERIES_INTRADAY', 'TIME_SERIES_DAILY', 'TIME_SERIES_WEEKLY', 'TIME_SERIES_MONTHLY', 'TIME_SERIES_DAILY_ADJUSTED', 'TIME_SERIES_WEEKLY_ADJUSTED', 'TIME_SERIES_MONTHLY_ADJUSTED'] | The time series of your choice.  | TIME_SERIES_DAILY | True |
| period | Union[Literal['intraday', 'daily', 'weekly', 'monthly']] | Period of the data to return. | daily | True |
| interval | Union[Literal['1min', '5min', '15min', '30min', '60min']] | Data granularity. | 60min | True |
| adjusted | Union[bool] | Output time series is adjusted by historical split and dividend events. | False | True |
| extended_hours | Union[bool] | Extended trading hours during pre-market and after-hours. | False | True |
| month | Union[str] | Query a specific month in history (in YYYY-MM format). | None | True |
| outputsize | Union[Literal['compact', 'full']] | Compact returns only the latest 100 data points in the intraday time series; full returns trailing 30 days of the most recent intraday data if the month parameter (see above) is not specified, or the full intraday data for a specific month in history if the month parameter is specified. | full | True |
</TabItem>

<TabItem value='cboe' label='cboe'>

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| symbol | Union[str, List[str]] | Symbol to get data for. |  | False |
| start_date | Union[date, str] | Start date of the data, in YYYY-MM-DD format. | None | True |
| end_date | Union[date, str] | End date of the data, in YYYY-MM-DD format. | None | True |
| chart | bool | Whether to create a chart or not, by default False. | False | True |
| provider | Union[Literal['alpha_vantage', 'cboe', 'fmp', 'intrinio', 'polygon', 'yfinance']] | The provider to use for the query, by default None. If None, the provider specified in defaults is selected or 'alpha_vantage' if there is no default. | alpha_vantage | True |
| interval | Union[Literal['1d', '1m']] | Data granularity. | 1d | True |
</TabItem>

<TabItem value='fmp' label='fmp'>

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| symbol | Union[str, List[str]] | Symbol to get data for. |  | False |
| start_date | Union[date, str] | Start date of the data, in YYYY-MM-DD format. | None | True |
| end_date | Union[date, str] | End date of the data, in YYYY-MM-DD format. | None | True |
| chart | bool | Whether to create a chart or not, by default False. | False | True |
| provider | Union[Literal['alpha_vantage', 'cboe', 'fmp', 'intrinio', 'polygon', 'yfinance']] | The provider to use for the query, by default None. If None, the provider specified in defaults is selected or 'alpha_vantage' if there is no default. | alpha_vantage | True |
| timeseries | Union[typing_extensions.Annotated[int, Ge(ge=0)]] | Number of days to look back. | None | True |
| interval | Literal['1min', '5min', '15min', '30min', '1hour', '4hour', '1day'] | Data granularity. | 1day | True |
</TabItem>

<TabItem value='intrinio' label='intrinio'>

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| symbol | Union[str, List[str]] | Symbol to get data for. |  | False |
| start_date | Union[date, str] | Start date of the data, in YYYY-MM-DD format. | None | True |
| end_date | Union[date, str] | End date of the data, in YYYY-MM-DD format. | None | True |
| chart | bool | Whether to create a chart or not, by default False. | False | True |
| provider | Union[Literal['alpha_vantage', 'cboe', 'fmp', 'intrinio', 'polygon', 'yfinance']] | The provider to use for the query, by default None. If None, the provider specified in defaults is selected or 'alpha_vantage' if there is no default. | alpha_vantage | True |
| timezone | Union[Literal['Africa/Algiers', 'Africa/Cairo', 'Africa/Casablanca', 'Africa/Harare', 'Africa/Johannesburg', 'Africa/Monrovia', 'Africa/Nairobi', 'America/Argentina/Buenos_Aires', 'America/Bogota', 'America/Caracas', 'America/Chicago', 'America/Chihuahua', 'America/Denver', 'America/Godthab', 'America/Guatemala', 'America/Guyana', 'America/Halifax', 'America/Indiana/Indianapolis', 'America/Juneau', 'America/La_Paz', 'America/Lima', 'America/Lima', 'America/Los_Angeles', 'America/Mazatlan', 'America/Mexico_City', 'America/Mexico_City', 'America/Monterrey', 'America/Montevideo', 'America/New_York', 'America/Phoenix', 'America/Regina', 'America/Santiago', 'America/Sao_Paulo', 'America/St_Johns', 'America/Tijuana', 'Asia/Almaty', 'Asia/Baghdad', 'Asia/Baku', 'Asia/Bangkok', 'Asia/Bangkok', 'Asia/Chongqing', 'Asia/Colombo', 'Asia/Dhaka', 'Asia/Dhaka', 'Asia/Hong_Kong', 'Asia/Irkutsk', 'Asia/Jakarta', 'Asia/Jerusalem', 'Asia/Kabul', 'Asia/Kamchatka', 'Asia/Karachi', 'Asia/Karachi', 'Asia/Kathmandu', 'Asia/Kolkata', 'Asia/Kolkata', 'Asia/Kolkata', 'Asia/Kolkata', 'Asia/Krasnoyarsk', 'Asia/Kuala_Lumpur', 'Asia/Kuwait', 'Asia/Magadan', 'Asia/Muscat', 'Asia/Muscat', 'Asia/Novosibirsk', 'Asia/Rangoon', 'Asia/Riyadh', 'Asia/Seoul', 'Asia/Shanghai', 'Asia/Singapore', 'Asia/Srednekolymsk', 'Asia/Taipei', 'Asia/Tashkent', 'Asia/Tbilisi', 'Asia/Tehran', 'Asia/Tokyo', 'Asia/Tokyo', 'Asia/Tokyo', 'Asia/Ulaanbaatar', 'Asia/Urumqi', 'Asia/Vladivostok', 'Asia/Yakutsk', 'Asia/Yekaterinburg', 'Asia/Yerevan', 'Atlantic/Azores', 'Atlantic/Cape_Verde', 'Atlantic/South_Georgia', 'Australia/Adelaide', 'Australia/Brisbane', 'Australia/Darwin', 'Australia/Hobart', 'Australia/Melbourne', 'Australia/Melbourne', 'Australia/Perth', 'Australia/Sydney', 'Etc/UTC', 'UTC', 'Europe/Amsterdam', 'Europe/Athens', 'Europe/Belgrade', 'Europe/Berlin', 'Europe/Berlin', 'Europe/Bratislava', 'Europe/Brussels', 'Europe/Bucharest', 'Europe/Budapest', 'Europe/Copenhagen', 'Europe/Dublin', 'Europe/Helsinki', 'Europe/Istanbul', 'Europe/Kaliningrad', 'Europe/Kiev', 'Europe/Lisbon', 'Europe/Ljubljana', 'Europe/London', 'Europe/London', 'Europe/Madrid', 'Europe/Minsk', 'Europe/Moscow', 'Europe/Moscow', 'Europe/Paris', 'Europe/Prague', 'Europe/Riga', 'Europe/Rome', 'Europe/Samara', 'Europe/Sarajevo', 'Europe/Skopje', 'Europe/Sofia', 'Europe/Stockholm', 'Europe/Tallinn', 'Europe/Vienna', 'Europe/Vilnius', 'Europe/Volgograd', 'Europe/Warsaw', 'Europe/Zagreb', 'Pacific/Apia', 'Pacific/Auckland', 'Pacific/Auckland', 'Pacific/Chatham', 'Pacific/Fakaofo', 'Pacific/Fiji', 'Pacific/Guadalcanal', 'Pacific/Guam', 'Pacific/Honolulu', 'Pacific/Majuro', 'Pacific/Midway', 'Pacific/Midway', 'Pacific/Noumea', 'Pacific/Pago_Pago', 'Pacific/Port_Moresby', 'Pacific/Tongatapu']] | Returns trading times in this timezone. | UTC | True |
| source | Union[Literal['realtime', 'delayed', 'nasdaq_basic']] | The source of the data. | realtime | True |
| start_time | Union[datetime.time] | Return intervals starting at the specified time on the `start_date` formatted as 'hh:mm:ss'. | None | True |
| end_time | Union[datetime.time] | Return intervals stopping at the specified time on the `end_date` formatted as 'hh:mm:ss'. | None | True |
| interval_size | Union[Literal['1m', '5m', '10m', '15m', '30m', '60m', '1h']] | The data time frequency. | 60m | True |
</TabItem>

<TabItem value='polygon' label='polygon'>

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| symbol | Union[str, List[str]] | Symbol to get data for. |  | False |
| start_date | Union[date, str] | Start date of the data, in YYYY-MM-DD format. | None | True |
| end_date | Union[date, str] | End date of the data, in YYYY-MM-DD format. | None | True |
| chart | bool | Whether to create a chart or not, by default False. | False | True |
| provider | Union[Literal['alpha_vantage', 'cboe', 'fmp', 'intrinio', 'polygon', 'yfinance']] | The provider to use for the query, by default None. If None, the provider specified in defaults is selected or 'alpha_vantage' if there is no default. | alpha_vantage | True |
| multiplier | int | Multiplier of the timespan. | 1 | True |
| timespan | Literal['minute', 'hour', 'day', 'week', 'month', 'quarter', 'year'] | Timespan of the data. | day | True |
| sort | Literal['asc', 'desc'] | Sort order of the data. | desc | True |
| limit | int | The number of data entries to return. | 49999 | True |
| adjusted | bool | Output time series is adjusted by historical split and dividend events. | True | True |
</TabItem>

<TabItem value='yfinance' label='yfinance'>

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| symbol | Union[str, List[str]] | Symbol to get data for. |  | False |
| start_date | Union[date, str] | Start date of the data, in YYYY-MM-DD format. | None | True |
| end_date | Union[date, str] | End date of the data, in YYYY-MM-DD format. | None | True |
| chart | bool | Whether to create a chart or not, by default False. | False | True |
| provider | Union[Literal['alpha_vantage', 'cboe', 'fmp', 'intrinio', 'polygon', 'yfinance']] | The provider to use for the query, by default None. If None, the provider specified in defaults is selected or 'alpha_vantage' if there is no default. | alpha_vantage | True |
| interval | Union[Literal['1m', '2m', '5m', '15m', '30m', '60m', '90m', '1h', '1d', '5d', '1wk', '1mo', '3mo']] | Data granularity. | 1d | True |
| period | Union[Literal['1d', '5d', '1mo', '3mo', '6mo', '1y', '2y', '5y', '10y', 'ytd', 'max']] | Period of the data to return. | max | True |
| prepost | bool | Include Pre and Post market data. | False | True |
| actions | bool | Include actions. | True | True |
| auto_adjust | bool | Adjust all OHLC data automatically. | False | True |
| back_adjust | bool | Attempt to adjust all the data automatically. | False | True |
| progress | bool | Show progress bar. | False | True |
| ignore_tz | bool | When combining from different timezones, ignore that part of datetime. | True | True |
| rounding | bool | Round to two decimal places? | True | True |
| repair | bool | Detect currency unit 100x mixups and attempt repair. | False | True |
| keepna | bool | Keep NaN rows returned by Yahoo? | False | True |
| group_by | Literal['ticker', 'column'] | Group by ticker or column. | column | True |
</TabItem>

</Tabs>

---

## Returns

```python wordwrap
OBBject
    results : List[StockHistorical]
        Serializable results.

    provider : Optional[Literal[Union[Literal['alpha_vantage', 'cboe', 'fmp', 'intrinio', 'polygon', 'yfinance'], NoneType]]
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
| date | datetime | The date of the data. |
| open | float | The open price of the symbol. |
| high | float | The high price of the symbol. |
| low | float | The low price of the symbol. |
| close | float | The close price of the symbol. |
| volume | Union[float, int] | The volume of the symbol. |
| vwap | Union[typing_extensions.Annotated[float, Gt(gt=0)]] | Volume Weighted Average Price of the symbol. |
</TabItem>

<TabItem value='alpha_vantage' label='alpha_vantage'>

| Name | Type | Description |
| ---- | ---- | ----------- |
| date | datetime | The date of the data. |
| open | float | The open price of the symbol. |
| high | float | The high price of the symbol. |
| low | float | The low price of the symbol. |
| close | float | The close price of the symbol. |
| volume | Union[float, int] | The volume of the symbol. |
| vwap | Union[typing_extensions.Annotated[float, Gt(gt=0)]] | Volume Weighted Average Price of the symbol. |
| adj_close | Union[typing_extensions.Annotated[float, Gt(gt=0)]] | The adjusted close price of the symbol. |
| dividend_amount | Union[typing_extensions.Annotated[float, Ge(ge=0)]] | Dividend amount paid for the corresponding date. |
| split_coefficient | Union[typing_extensions.Annotated[float, Ge(ge=0)]] | Split coefficient for the corresponding date. |
</TabItem>

<TabItem value='cboe' label='cboe'>

| Name | Type | Description |
| ---- | ---- | ----------- |
| date | datetime | The date of the data. |
| open | float | The open price of the symbol. |
| high | float | The high price of the symbol. |
| low | float | The low price of the symbol. |
| close | float | The close price of the symbol. |
| volume | Union[float, int] | The volume of the symbol. |
| vwap | Union[typing_extensions.Annotated[float, Gt(gt=0)]] | Volume Weighted Average Price of the symbol. |
| calls_volume | Union[float] | Number of calls traded during the most recent trading period. Only valid if interval is 1m. |
| puts_volume | Union[float] | Number of puts traded during the most recent trading period. Only valid if interval is 1m. |
| total_options_volume | Union[float] | Total number of options traded during the most recent trading period. Only valid if interval is 1m. |
</TabItem>

<TabItem value='fmp' label='fmp'>

| Name | Type | Description |
| ---- | ---- | ----------- |
| date | datetime | The date of the data. |
| open | float | The open price of the symbol. |
| high | float | The high price of the symbol. |
| low | float | The low price of the symbol. |
| close | float | The close price of the symbol. |
| volume | Union[float, int] | The volume of the symbol. |
| vwap | Union[typing_extensions.Annotated[float, Gt(gt=0)]] | Volume Weighted Average Price of the symbol. |
| adj_close | Union[float] | Adjusted Close Price of the symbol. |
| unadjusted_volume | Union[float] | Unadjusted volume of the symbol. |
| change | Union[float] | Change in the price of the symbol from the previous day. |
| change_percent | Union[float] | Change % in the price of the symbol. |
| label | Union[str] | Human readable format of the date. |
| change_over_time | Union[float] | Change % in the price of the symbol over a period of time. |
</TabItem>

<TabItem value='intrinio' label='intrinio'>

| Name | Type | Description |
| ---- | ---- | ----------- |
| date | datetime | The date of the data. |
| open | float | The open price of the symbol. |
| high | float | The high price of the symbol. |
| low | float | The low price of the symbol. |
| close | float | The close price of the symbol. |
| volume | Union[float, int] | The volume of the symbol. |
| vwap | Union[typing_extensions.Annotated[float, Gt(gt=0)]] | Volume Weighted Average Price of the symbol. |
| close_time | Union[datetime] | The timestamp that represents the end of the interval span. |
| interval | Union[str] | The data time frequency. |
| average | Union[float] | Average trade price of an individual stock during the interval. |
| change | Union[float] | Change in the price of the symbol from the previous day. |
</TabItem>

<TabItem value='polygon' label='polygon'>

| Name | Type | Description |
| ---- | ---- | ----------- |
| date | datetime | The date of the data. |
| open | float | The open price of the symbol. |
| high | float | The high price of the symbol. |
| low | float | The low price of the symbol. |
| close | float | The close price of the symbol. |
| volume | Union[float, int] | The volume of the symbol. |
| vwap | Union[typing_extensions.Annotated[float, Gt(gt=0)]] | Volume Weighted Average Price of the symbol. |
| transactions | Union[typing_extensions.Annotated[int, Gt(gt=0)]] | Number of transactions for the symbol in the time period. |
</TabItem>

</Tabs>

