---
title: quote
description: OpenBB Platform Function
---

import Tabs from '@theme/Tabs';
import TabItem from '@theme/TabItem';

# quote

Load stock data for a specific ticker.

```python wordwrap
quote(symbol: Union[str, List[str]], provider: Literal[str] = fmp)
```

---

## Parameters

<Tabs>
<TabItem value="standard" label="Standard">

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| symbol | Union[str, List[str]] | Symbol to get data for. |  | False |
| provider | Literal['fmp'] | The provider to use for the query, by default None. If None, the provider specified in defaults is selected or 'fmp' if there is no default. | fmp | True |
</TabItem>

</Tabs>

---

## Returns

```python wordwrap
OBBject
    results : List[StockQuote]
        Serializable results.

    provider : Optional[Literal['fmp']]
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
| day_low | float | Lowest price of the stock in the current trading day. |
| day_high | float | Highest price of the stock in the current trading day. |
| date | datetime | Timestamp of the stock quote. |
</TabItem>

<TabItem value='fmp' label='fmp'>

| Name | Type | Description |
| ---- | ---- | ----------- |
| symbol | str | Symbol of the company. |
| name | str | Name of the company. |
| price | float | Current trading price of the stock. |
| changes_percentage | float | Change percentage of the stock price. |
| change | float | Change in the stock price. |
| year_high | float | Highest price of the stock in the last 52 weeks. |
| year_low | float | Lowest price of the stock in the last 52 weeks. |
| market_cap | float | Market cap of the company. |
| price_avg50 | float | 50 days average price of the stock. |
| price_avg200 | float | 200 days average price of the stock. |
| volume | int | Volume of the stock in the current trading day. |
| avg_volume | int | Average volume of the stock in the last 10 trading days. |
| exchange | str | Exchange the stock is traded on. |
| open | float | Opening price of the stock in the current trading day. |
| previous_close | float | Previous closing price of the stock. |
| eps | float | Earnings per share of the stock. |
| pe | float | Price earnings ratio of the stock. |
| earnings_announcement | str | Earnings announcement date of the stock. |
| shares_outstanding | int | Number of shares outstanding of the stock. |
</TabItem>

</Tabs>

