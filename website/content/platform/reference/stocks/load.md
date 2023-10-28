---
title: load
description: Information related to the 'load' function for obtaining stock historical
  price data for specific ticker symbols. Covering parameters, returns, and data across
  the standard, 'fmp', 'intrinio', and 'polygon' functions.
keywords:
- Docusaurus
- SEO
- metadata
- load function
- stock historical price
- ticker symbols
- fmp
- intrinio
- polygon
- stock data
- parameters
- returns
- open price
- high price
- low price
- close price
- volume
- vwap
- Volume Weighted Average Price
- start date
- end date
- provider
- timeseries
- data granularity
- timezone
- interval size
- multiplier
- timespan
- sort order
- data entries
- adjusted
- trading times
- data source
- interval starting and stopping time
- data time frequency
- adjusted close price
- unadjusted volume
- price change
- change over time
- average trade price
- transaction numbers
---

import HeadTitle from '@site/src/components/General/HeadTitle.tsx';

<HeadTitle title="stocks.load - Reference | OpenBB Platform Docs" />

import Tabs from '@theme/Tabs';
import TabItem from '@theme/TabItem';

# load

Stock Historical price. Load stock data for a specific ticker.

```python wordwrap
load(symbol: Union[str, List[str]], start_date: Union[date, str] = None, end_date: Union[date, str] = None, provider: Literal[str] = fmp)
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
| provider | Literal['fmp', 'intrinio', 'polygon'] | The provider to use for the query, by default None. If None, the provider specified in defaults is selected or 'fmp' if there is no default. | fmp | True |
</TabItem>

<TabItem value='fmp' label='fmp'>

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| symbol | Union[str, List[str]] | Symbol to get data for. |  | False |
| start_date | Union[date, str] | Start date of the data, in YYYY-MM-DD format. | None | True |
| end_date | Union[date, str] | End date of the data, in YYYY-MM-DD format. | None | True |
| provider | Literal['fmp', 'intrinio', 'polygon'] | The provider to use for the query, by default None. If None, the provider specified in defaults is selected or 'fmp' if there is no default. | fmp | True |
| timeseries | int | Number of days to look back. | None | True |
| interval | Literal['1min', '5min', '15min', '30min', '1hour', '4hour', '1day'] | Data granularity. | 1day | True |
</TabItem>

<TabItem value='intrinio' label='intrinio'>

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| symbol | Union[str, List[str]] | Symbol to get data for. |  | False |
| start_date | Union[date, str] | Start date of the data, in YYYY-MM-DD format. | None | True |
| end_date | Union[date, str] | End date of the data, in YYYY-MM-DD format. | None | True |
| provider | Literal['fmp', 'intrinio', 'polygon'] | The provider to use for the query, by default None. If None, the provider specified in defaults is selected or 'fmp' if there is no default. | fmp | True |
| timezone | Literal['Africa/Algiers', 'Africa/Cairo', 'Africa/Casablanca', 'Africa/Harare', 'Africa/Johannesburg', 'Africa/Monrovia', 'Africa/Nairobi', 'America/Argentina/Buenos_Aires', 'America/Bogota', 'America/Caracas', 'America/Chicago', 'America/Chihuahua', 'America/Denver', 'America/Godthab', 'America/Guatemala', 'America/Guyana', 'America/Halifax', 'America/Indiana/Indianapolis', 'America/Juneau', 'America/La_Paz', 'America/Lima', 'America/Los_Angeles', 'America/Mazatlan', 'America/Mexico_City', 'America/Monterrey', 'America/Montevideo', 'America/New_York', 'America/Phoenix', 'America/Regina', 'America/Santiago', 'America/Sao_Paulo', 'America/St_Johns', 'America/Tijuana', 'Asia/Almaty', 'Asia/Baghdad', 'Asia/Baku', 'Asia/Bangkok', 'Asia/Chongqing', 'Asia/Colombo', 'Asia/Dhaka', 'Asia/Hong_Kong', 'Asia/Irkutsk', 'Asia/Jakarta', 'Asia/Jerusalem', 'Asia/Kabul', 'Asia/Kamchatka', 'Asia/Karachi', 'Asia/Kathmandu', 'Asia/Kolkata', 'Asia/Krasnoyarsk', 'Asia/Kuala_Lumpur', 'Asia/Kuwait', 'Asia/Magadan', 'Asia/Muscat', 'Asia/Novosibirsk', 'Asia/Rangoon', 'Asia/Riyadh', 'Asia/Seoul', 'Asia/Shanghai', 'Asia/Singapore', 'Asia/Srednekolymsk', 'Asia/Taipei', 'Asia/Tashkent', 'Asia/Tbilisi', 'Asia/Tehran', 'Asia/Tokyo', 'Asia/Ulaanbaatar', 'Asia/Urumqi', 'Asia/Vladivostok', 'Asia/Yakutsk', 'Asia/Yekaterinburg', 'Asia/Yerevan', 'Atlantic/Azores', 'Atlantic/Cape_Verde', 'Atlantic/South_Georgia', 'Australia/Adelaide', 'Australia/Brisbane', 'Australia/Darwin', 'Australia/Hobart', 'Australia/Melbourne', 'Australia/Perth', 'Australia/Sydney', 'Etc/UTC', 'UTC', 'Europe/Amsterdam', 'Europe/Athens', 'Europe/Belgrade', 'Europe/Berlin', 'Europe/Bratislava', 'Europe/Brussels', 'Europe/Bucharest', 'Europe/Budapest', 'Europe/Copenhagen', 'Europe/Dublin', 'Europe/Helsinki', 'Europe/Istanbul', 'Europe/Kaliningrad', 'Europe/Kiev', 'Europe/Lisbon', 'Europe/Ljubljana', 'Europe/London', 'Europe/Madrid', 'Europe/Minsk', 'Europe/Moscow', 'Europe/Paris', 'Europe/Prague', 'Europe/Riga', 'Europe/Rome', 'Europe/Samara', 'Europe/Sarajevo', 'Europe/Skopje', 'Europe/Sofia', 'Europe/Stockholm', 'Europe/Tallinn', 'Europe/Vienna', 'Europe/Vilnius', 'Europe/Volgograd', 'Europe/Warsaw', 'Europe/Zagreb', 'Pacific/Apia', 'Pacific/Auckland', 'Pacific/Chatham', 'Pacific/Fakaofo', 'Pacific/Fiji', 'Pacific/Guadalcanal', 'Pacific/Guam', 'Pacific/Honolulu', 'Pacific/Majuro', 'Pacific/Midway', 'Pacific/Noumea', 'Pacific/Pago_Pago', 'Pacific/Port_Moresby', 'Pacific/Tongatapu'] | Returns trading times in this timezone. | UTC | True |
| source | Literal['realtime', 'delayed', 'nasdaq_basic'] | The source of the data. | realtime | True |
| start_time | datetime.time | Return intervals starting at the specified time on the `start_date` formatted as 'hh:mm:ss'. | None | True |
| end_time | datetime.time | Return intervals stopping at the specified time on the `end_date` formatted as 'hh:mm:ss'. | None | True |
| interval_size | Literal['1m', '5m', '10m', '15m', '30m', '60m', '1h'] | The data time frequency. | 60m | True |
</TabItem>

<TabItem value='polygon' label='polygon'>

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| symbol | Union[str, List[str]] | Symbol to get data for. |  | False |
| start_date | Union[date, str] | Start date of the data, in YYYY-MM-DD format. | None | True |
| end_date | Union[date, str] | End date of the data, in YYYY-MM-DD format. | None | True |
| provider | Literal['fmp', 'intrinio', 'polygon'] | The provider to use for the query, by default None. If None, the provider specified in defaults is selected or 'fmp' if there is no default. | fmp | True |
| multiplier | int | Multiplier of the timespan. | 1 | True |
| timespan | Literal['minute', 'hour', 'day', 'week', 'month', 'quarter', 'year'] | Timespan of the data. | day | True |
| sort | Literal['asc', 'desc'] | Sort order of the data. | desc | True |
| limit | int | The number of data entries to return. | 49999 | True |
| adjusted | bool | Output time series is adjusted by historical split and dividend events. | True | True |
</TabItem>

</Tabs>

---

## Returns

```python wordwrap
OBBject
    results : List[StockHistorical]
        Serializable results.

    provider : Optional[Literal['fmp', 'intrinio', 'polygon']]
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
| vwap | float | Volume Weighted Average Price of the symbol. |
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
| vwap | float | Volume Weighted Average Price of the symbol. |
| adj_close | float | Adjusted Close Price of the symbol. |
| unadjusted_volume | float | Unadjusted volume of the symbol. |
| change | float | Change in the price of the symbol from the previous day. |
| change_percent | float | Change % in the price of the symbol. |
| label | str | Human readable format of the date. |
| change_over_time | float | Change % in the price of the symbol over a period of time. |
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
| vwap | float | Volume Weighted Average Price of the symbol. |
| close_time | datetime | The timestamp that represents the end of the interval span. |
| interval | str | The data time frequency. |
| average | float | Average trade price of an individual stock during the interval. |
| change | float | Change in the price of the symbol from the previous day. |
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
| vwap | float | Volume Weighted Average Price of the symbol. |
| transactions | int | Number of transactions for the symbol in the time period. |
</TabItem>

</Tabs>
