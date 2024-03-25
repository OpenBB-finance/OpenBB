---
title: "Equity Historical"
description: "Get historical price data for a given stock"
---

<!-- markdownlint-disable MD012 MD031 MD033 -->

import Tabs from '@theme/Tabs';
import TabItem from '@theme/TabItem';

---

## Implementation details

### Class names

| Model name | Parameters class | Data class |
| ---------- | ---------------- | ---------- |
| `EquityHistorical` | `EquityHistoricalQueryParams` | `EquityHistoricalData` |

### Import Statement

```python
from openbb_core.provider.standard_models.equity_historical import (
EquityHistoricalData,
EquityHistoricalQueryParams,
)
```

---

## Parameters

<Tabs>

<TabItem value='standard' label='standard'>

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| symbol | Union[str, List[str]] | Symbol to get data for. Multiple items allowed for provider(s): alpha_vantage, cboe, fmp, polygon, tiingo, tmx, tradier, yfinance. |  | False |
| interval | str | Time interval of the data to return. | 1d | True |
| start_date | Union[date, str] | Start date of the data, in YYYY-MM-DD format. | None | True |
| end_date | Union[date, str] | End date of the data, in YYYY-MM-DD format. | None | True |
| provider | Literal['alpha_vantage', 'cboe', 'fmp', 'intrinio', 'polygon', 'tiingo', 'tmx', 'tradier', 'yfinance'] | The provider to use for the query, by default None. If None, the provider specified in defaults is selected or 'alpha_vantage' if there is no default. | alpha_vantage | True |
</TabItem>

<TabItem value='alpha_vantage' label='alpha_vantage'>

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| symbol | Union[str, List[str]] | Symbol to get data for. Multiple items allowed for provider(s): alpha_vantage, cboe, fmp, polygon, tiingo, tmx, tradier, yfinance. |  | False |
| interval | str | Time interval of the data to return. | 1d | True |
| start_date | Union[date, str] | Start date of the data, in YYYY-MM-DD format. | None | True |
| end_date | Union[date, str] | End date of the data, in YYYY-MM-DD format. | None | True |
| provider | Literal['alpha_vantage', 'cboe', 'fmp', 'intrinio', 'polygon', 'tiingo', 'tmx', 'tradier', 'yfinance'] | The provider to use for the query, by default None. If None, the provider specified in defaults is selected or 'alpha_vantage' if there is no default. | alpha_vantage | True |
| adjustment | Literal['splits_only', 'splits_and_dividends', 'unadjusted'] | The adjustment factor to apply. 'splits_only' is not supported for intraday data. | splits_only | True |
| extended_hours | bool | Include Pre and Post market data. | False | True |
| adjusted | bool | This field is deprecated (4.1.5) and will be removed in a future version. Use 'adjustment' set as 'splits_and_dividends' instead. | False | True |
</TabItem>

<TabItem value='cboe' label='cboe'>

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| symbol | Union[str, List[str]] | Symbol to get data for. Multiple items allowed for provider(s): alpha_vantage, cboe, fmp, polygon, tiingo, tmx, tradier, yfinance. |  | False |
| interval | str | Time interval of the data to return. | 1d | True |
| start_date | Union[date, str] | Start date of the data, in YYYY-MM-DD format. | None | True |
| end_date | Union[date, str] | End date of the data, in YYYY-MM-DD format. | None | True |
| provider | Literal['alpha_vantage', 'cboe', 'fmp', 'intrinio', 'polygon', 'tiingo', 'tmx', 'tradier', 'yfinance'] | The provider to use for the query, by default None. If None, the provider specified in defaults is selected or 'alpha_vantage' if there is no default. | alpha_vantage | True |
| use_cache | bool | When True, the company directories will be cached for 24 hours and are used to validate symbols. The results of the function are not cached. Set as False to bypass. | True | True |
</TabItem>

<TabItem value='fmp' label='fmp'>

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| symbol | Union[str, List[str]] | Symbol to get data for. Multiple items allowed for provider(s): alpha_vantage, cboe, fmp, polygon, tiingo, tmx, tradier, yfinance. |  | False |
| interval | str | Time interval of the data to return. | 1d | True |
| start_date | Union[date, str] | Start date of the data, in YYYY-MM-DD format. | None | True |
| end_date | Union[date, str] | End date of the data, in YYYY-MM-DD format. | None | True |
| provider | Literal['alpha_vantage', 'cboe', 'fmp', 'intrinio', 'polygon', 'tiingo', 'tmx', 'tradier', 'yfinance'] | The provider to use for the query, by default None. If None, the provider specified in defaults is selected or 'alpha_vantage' if there is no default. | alpha_vantage | True |
</TabItem>

<TabItem value='intrinio' label='intrinio'>

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| symbol | Union[str, List[str]] | Symbol to get data for. Multiple items allowed for provider(s): alpha_vantage, cboe, fmp, polygon, tiingo, tmx, tradier, yfinance. |  | False |
| interval | str | Time interval of the data to return. | 1d | True |
| start_date | Union[date, str] | Start date of the data, in YYYY-MM-DD format. | None | True |
| end_date | Union[date, str] | End date of the data, in YYYY-MM-DD format. | None | True |
| provider | Literal['alpha_vantage', 'cboe', 'fmp', 'intrinio', 'polygon', 'tiingo', 'tmx', 'tradier', 'yfinance'] | The provider to use for the query, by default None. If None, the provider specified in defaults is selected or 'alpha_vantage' if there is no default. | alpha_vantage | True |
| start_time | datetime.time | Return intervals starting at the specified time on the `start_date` formatted as 'HH:MM:SS'. | None | True |
| end_time | datetime.time | Return intervals stopping at the specified time on the `end_date` formatted as 'HH:MM:SS'. | None | True |
| timezone | str | Timezone of the data, in the IANA format (Continent/City). | America/New_York | True |
| source | Literal['realtime', 'delayed', 'nasdaq_basic'] | The source of the data. | realtime | True |
</TabItem>

<TabItem value='polygon' label='polygon'>

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| symbol | Union[str, List[str]] | Symbol to get data for. Multiple items allowed for provider(s): alpha_vantage, cboe, fmp, polygon, tiingo, tmx, tradier, yfinance. |  | False |
| interval | str | Time interval of the data to return. | 1d | True |
| start_date | Union[date, str] | Start date of the data, in YYYY-MM-DD format. | None | True |
| end_date | Union[date, str] | End date of the data, in YYYY-MM-DD format. | None | True |
| provider | Literal['alpha_vantage', 'cboe', 'fmp', 'intrinio', 'polygon', 'tiingo', 'tmx', 'tradier', 'yfinance'] | The provider to use for the query, by default None. If None, the provider specified in defaults is selected or 'alpha_vantage' if there is no default. | alpha_vantage | True |
| adjustment | Literal['splits_only', 'unadjusted'] | The adjustment factor to apply. Default is splits only. | splits_only | True |
| extended_hours | bool | Include Pre and Post market data. | False | True |
| sort | Literal['asc', 'desc'] | Sort order of the data. This impacts the results in combination with the 'limit' parameter. The results are always returned in ascending order by date. | asc | True |
| limit | int | The number of data entries to return. | 49999 | True |
</TabItem>

<TabItem value='tiingo' label='tiingo'>

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| symbol | Union[str, List[str]] | Symbol to get data for. Multiple items allowed for provider(s): alpha_vantage, cboe, fmp, polygon, tiingo, tmx, tradier, yfinance. |  | False |
| interval | str | Time interval of the data to return. | 1d | True |
| start_date | Union[date, str] | Start date of the data, in YYYY-MM-DD format. | None | True |
| end_date | Union[date, str] | End date of the data, in YYYY-MM-DD format. | None | True |
| provider | Literal['alpha_vantage', 'cboe', 'fmp', 'intrinio', 'polygon', 'tiingo', 'tmx', 'tradier', 'yfinance'] | The provider to use for the query, by default None. If None, the provider specified in defaults is selected or 'alpha_vantage' if there is no default. | alpha_vantage | True |
</TabItem>

<TabItem value='tmx' label='tmx'>

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| symbol | Union[str, List[str]] | Symbol to get data for. Multiple items allowed for provider(s): alpha_vantage, cboe, fmp, polygon, tiingo, tmx, tradier, yfinance. |  | False |
| interval | str | Time interval of the data to return. | 1d | True |
| start_date | Union[date, str] | Start date of the data, in YYYY-MM-DD format. | None | True |
| end_date | Union[date, str] | End date of the data, in YYYY-MM-DD format. | None | True |
| provider | Literal['alpha_vantage', 'cboe', 'fmp', 'intrinio', 'polygon', 'tiingo', 'tmx', 'tradier', 'yfinance'] | The provider to use for the query, by default None. If None, the provider specified in defaults is selected or 'alpha_vantage' if there is no default. | alpha_vantage | True |
| adjustment | Literal['splits_only', 'splits_and_dividends', 'unadjusted'] | The adjustment factor to apply. Only valid for daily data. | splits_only | True |
</TabItem>

<TabItem value='tradier' label='tradier'>

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| symbol | Union[str, List[str]] | Symbol to get data for. Multiple items allowed for provider(s): alpha_vantage, cboe, fmp, polygon, tiingo, tmx, tradier, yfinance. |  | False |
| interval | str | Time interval of the data to return. | 1d | True |
| start_date | Union[date, str] | Start date of the data, in YYYY-MM-DD format. | None | True |
| end_date | Union[date, str] | End date of the data, in YYYY-MM-DD format. | None | True |
| provider | Literal['alpha_vantage', 'cboe', 'fmp', 'intrinio', 'polygon', 'tiingo', 'tmx', 'tradier', 'yfinance'] | The provider to use for the query, by default None. If None, the provider specified in defaults is selected or 'alpha_vantage' if there is no default. | alpha_vantage | True |
| extended_hours | bool | Include Pre and Post market data. | False | True |
</TabItem>

<TabItem value='yfinance' label='yfinance'>

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| symbol | Union[str, List[str]] | Symbol to get data for. Multiple items allowed for provider(s): alpha_vantage, cboe, fmp, polygon, tiingo, tmx, tradier, yfinance. |  | False |
| interval | str | Time interval of the data to return. | 1d | True |
| start_date | Union[date, str] | Start date of the data, in YYYY-MM-DD format. | None | True |
| end_date | Union[date, str] | End date of the data, in YYYY-MM-DD format. | None | True |
| provider | Literal['alpha_vantage', 'cboe', 'fmp', 'intrinio', 'polygon', 'tiingo', 'tmx', 'tradier', 'yfinance'] | The provider to use for the query, by default None. If None, the provider specified in defaults is selected or 'alpha_vantage' if there is no default. | alpha_vantage | True |
| extended_hours | bool | Include Pre and Post market data. | False | True |
| include_actions | bool | Include dividends and stock splits in results. | True | True |
| adjustment | Literal['splits_only', 'splits_and_dividends'] | The adjustment factor to apply. Default is splits only. | splits_only | True |
| adjusted | bool | This field is deprecated (4.1.5) and will be removed in a future version. Use 'adjustment' set as 'splits_and_dividends' instead. | False | True |
| prepost | bool | This field is deprecated (4.1.5) and will be removed in a future version. Use 'extended_hours' as True instead. | False | True |
</TabItem>

</Tabs>

---

## Data

<Tabs>

<TabItem value='standard' label='standard'>

| Name | Type | Description |
| ---- | ---- | ----------- |
| date | Union[date, datetime] | The date of the data. |
| open | float | The open price. |
| high | float | The high price. |
| low | float | The low price. |
| close | float | The close price. |
| volume | Union[float, int] | The trading volume. |
| vwap | float | Volume Weighted Average Price over the period. |
</TabItem>

<TabItem value='alpha_vantage' label='alpha_vantage'>

| Name | Type | Description |
| ---- | ---- | ----------- |
| date | Union[date, datetime] | The date of the data. |
| open | float | The open price. |
| high | float | The high price. |
| low | float | The low price. |
| close | float | The close price. |
| volume | Union[float, int] | The trading volume. |
| vwap | float | Volume Weighted Average Price over the period. |
| adj_close | float, Gt(gt=0) | The adjusted close price. |
| dividend | float, Ge(ge=0) | Dividend amount, if a dividend was paid. |
| split_ratio | float, Ge(ge=0) | Split coefficient, if a split occurred. |
</TabItem>

<TabItem value='cboe' label='cboe'>

| Name | Type | Description |
| ---- | ---- | ----------- |
| date | Union[date, datetime] | The date of the data. |
| open | float | The open price. |
| high | float | The high price. |
| low | float | The low price. |
| close | float | The close price. |
| volume | Union[float, int] | The trading volume. |
| vwap | float | Volume Weighted Average Price over the period. |
| calls_volume | int | Number of calls traded during the most recent trading period. Only valid if interval is 1m. |
| puts_volume | int | Number of puts traded during the most recent trading period. Only valid if interval is 1m. |
| total_options_volume | int | Total number of options traded during the most recent trading period. Only valid if interval is 1m. |
</TabItem>

<TabItem value='fmp' label='fmp'>

| Name | Type | Description |
| ---- | ---- | ----------- |
| date | Union[date, datetime] | The date of the data. |
| open | float | The open price. |
| high | float | The high price. |
| low | float | The low price. |
| close | float | The close price. |
| volume | Union[float, int] | The trading volume. |
| vwap | float | Volume Weighted Average Price over the period. |
| adj_close | float | The adjusted close price. |
| unadjusted_volume | float | Unadjusted volume of the symbol. |
| change | float | Change in the price from the previous close. |
| change_percent | float | Change in the price from the previous close, as a normalized percent. |
</TabItem>

<TabItem value='intrinio' label='intrinio'>

| Name | Type | Description |
| ---- | ---- | ----------- |
| date | Union[date, datetime] | The date of the data. |
| open | float | The open price. |
| high | float | The high price. |
| low | float | The low price. |
| close | float | The close price. |
| volume | Union[float, int] | The trading volume. |
| vwap | float | Volume Weighted Average Price over the period. |
| average | float | Average trade price of an individual equity during the interval. |
| change | float | Change in the price of the symbol from the previous day. |
| change_percent | float | Percent change in the price of the symbol from the previous day. |
| adj_open | float | The adjusted open price. |
| adj_high | float | The adjusted high price. |
| adj_low | float | The adjusted low price. |
| adj_close | float | The adjusted close price. |
| adj_volume | float | The adjusted volume. |
| fifty_two_week_high | float | 52 week high price for the symbol. |
| fifty_two_week_low | float | 52 week low price for the symbol. |
| factor | float | factor by which to multiply equity prices before this date, in order to calculate historically-adjusted equity prices. |
| split_ratio | float | Ratio of the equity split, if a split occurred. |
| dividend | float | Dividend amount, if a dividend was paid. |
| close_time | datetime | The timestamp that represents the end of the interval span. |
| interval | str | The data time frequency. |
| intra_period | bool | If true, the equity price represents an unfinished period (be it day, week, quarter, month, or year), meaning that the close price is the latest price available, not the official close price for the period |
</TabItem>

<TabItem value='polygon' label='polygon'>

| Name | Type | Description |
| ---- | ---- | ----------- |
| date | Union[date, datetime] | The date of the data. |
| open | float | The open price. |
| high | float | The high price. |
| low | float | The low price. |
| close | float | The close price. |
| volume | Union[float, int] | The trading volume. |
| vwap | float | Volume Weighted Average Price over the period. |
| transactions | int, Gt(gt=0) | Number of transactions for the symbol in the time period. |
</TabItem>

<TabItem value='tiingo' label='tiingo'>

| Name | Type | Description |
| ---- | ---- | ----------- |
| date | Union[date, datetime] | The date of the data. |
| open | float | The open price. |
| high | float | The high price. |
| low | float | The low price. |
| close | float | The close price. |
| volume | Union[float, int] | The trading volume. |
| vwap | float | Volume Weighted Average Price over the period. |
| adj_open | float | The adjusted open price. |
| adj_high | float | The adjusted high price. |
| adj_low | float | The adjusted low price. |
| adj_close | float | The adjusted close price. |
| adj_volume | float | The adjusted volume. |
| split_ratio | float | Ratio of the equity split, if a split occurred. |
| dividend | float | Dividend amount, if a dividend was paid. |
</TabItem>

<TabItem value='tmx' label='tmx'>

| Name | Type | Description |
| ---- | ---- | ----------- |
| date | Union[date, datetime] | The date of the data. |
| open | float | The open price. |
| high | float | The high price. |
| low | float | The low price. |
| close | float | The close price. |
| volume | Union[float, int] | The trading volume. |
| vwap | float | Volume Weighted Average Price over the period. |
| change | float | Change in price. |
| change_percent | float | Change in price, as a normalized percentage. |
| transactions | int | Total number of transactions recorded. |
| transactions_value | float | Nominal value of recorded transactions. |
</TabItem>

<TabItem value='tradier' label='tradier'>

| Name | Type | Description |
| ---- | ---- | ----------- |
| date | Union[date, datetime] | The date of the data. |
| open | float | The open price. |
| high | float | The high price. |
| low | float | The low price. |
| close | float | The close price. |
| volume | Union[float, int] | The trading volume. |
| vwap | float | Volume Weighted Average Price over the period. |
| last_price | float | The last price of the equity. |
</TabItem>

<TabItem value='yfinance' label='yfinance'>

| Name | Type | Description |
| ---- | ---- | ----------- |
| date | Union[date, datetime] | The date of the data. |
| open | float | The open price. |
| high | float | The high price. |
| low | float | The low price. |
| close | float | The close price. |
| volume | Union[float, int] | The trading volume. |
| vwap | float | Volume Weighted Average Price over the period. |
| split_ratio | float | Ratio of the equity split, if a split occurred. |
| dividend | float | Dividend amount (split-adjusted), if a dividend was paid. |
</TabItem>

</Tabs>

