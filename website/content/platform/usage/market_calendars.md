---
title: Market Calendars
sidebar_position: 5
description: This page provides details on the market calendars available in the OpenBB
  Platform.  Equity and economic calendars keep investors abreast of market activity and events.
  This guide provides examples for using the variety of calendars, and differences between sources.
keywords:
- stocks
- companies
- calendars
- earnings
- splits
- dividends
- ipo
- events
- economic calendar
- CPI report
- inflation
- expectations
- global
- central banks
- timezone
- tz-aware
- tz-unaware
- convert time
- ISM Manufacturing New Orders
- dividend yield
- analyst consensus
- EPS
---

import HeadTitle from '@site/src/components/General/HeadTitle.tsx';

<HeadTitle title="Market Calendars - Usage | OpenBB Platform Docs" />

Market calendars are an essential part of any analyst's daily rituals. Economic events and corporate actions provide near-term trading opportunities (or reasons to get out of the way) as expectations meet reality. The OpenBB Platform has a variety of calendars.

- Economic
- Earnings
- Dividends
- Splits
- IPO/SPOs

Let's take a look at some use-cases.

:::note
Examples on this page will assume that the OpenBB Platform is installed, the Python environment is active, and the Python interface has been imported into the active session.

```python
from openbb import obb
import pandas as pd
```

:::

## Economic Calendar

The economic calendar aggregates global central bank and macroeconomic releases, it is located within the `obb.economy` module.

:::tip
Do not rely on the economic calendar for real-time updates. Times posted are scheduled by publishers and are estimates which do not reflect the actual time data is released to the public.
:::

### Timezone Considerations

There are subtle differences between providers, the main consideration will be the timestamp. FMP and TradingEconomics both return the calendar as UTC-0, while Nasdaq posts events in US/Eastern time. Of the three, only TradingEconomics provides a TZ-aware timestamp. The differences can be reconciled with a few lines of code.

To identify the issue, let's look at one event.  First, from FMP:

```python
fmp_df = obb.economy.calendar(provider="fmp", start_date="2023-11-19", end_date="2023-11-20").to_df()
fmp_df[fmp_df["event"].str.contains("20-Year Bond Auction")]
```

 date                | country   | event                |   previous |   consensus | importance   | currency   |   change |   change_percent |
|:--------------------|:----------|:---------------------|-----------:|------------:|:-------------|:-----------|---------:|-----------------:|
| 2023-11-20 18:00:00 | US        | 20-Year Bond Auction |      5.245 |         nan | Low          | USD        |      nan |                0 |

Then Nasdaq:

```python
nasdaq_df = obb.economy.calendar(provider="nasdaq", start_date="2023-11-19", end_date="2023-11-20").to_df()
nasdaq_df[nasdaq_df["event"].str.contains("20-Year Bond Auction")]
```

| date                | country       | event                | actual   | previous   | consensus   |  description   |
|:--------------------|:--------------|:---------------------|:---------|:-----------|:------------|:----------------|
| 2023-11-20 13:00:00 | United States | 20-Year Bond Auction | -        | 5.245%     | -       | The figures displayed in the calendar represent the yield on the Treasury Bond auctioned. |

Now let's convert the FMP timestamp to US/Eastern time.

```python
from datetime import time

fmp_df.index = fmp_df.index.map(
    lambda dt: dt.tz_localize("UTC")
    .tz_convert("America/New_York")
    if dt.time() != time(0, 0, 0)
    else dt.tz_localize("America/New_York")
)
fmp_df[fmp_df["event"].str.contains("20-Year Bond Auction")]
```

| date                      | country   | event                |   previous |   consensus | importance   | currency   |   change |   change_percent |
|:--------------------------|:----------|:---------------------|-----------:|------------:|:-------------|:-----------|---------:|-----------------:|
| 2023-11-20 13:00:00-05:00 | US        | 20-Year Bond Auction |      5.245 |         nan | Low          | USD        |      nan |                0 |

Timestamps can be a factor with start/end dates because the calendar day will roll over at midnight, moving the date.  Converting the timestamp will overcome this, but be aware of when the time is `00:00:00`, signifying an all-day event like a holiday.

An exception was added in the code above to maintain the time where applicable, instead of rolling it back five hours.

For these reasons, among others, it is important for users to know and understand their data intimately.

### Filtering by Event

The providers do not have a pre-request filter for a specific event. TradingEconomics does have categories, like 'government', but that does not focus it on any particular release. To find something like PMI reports, search for it post-request.

FMP allows queries to this endpoint to be a maximum width of three months. To get the year-to-date events, requests will need to loop. The code below will do that, filter the results for ISM Manufacturing New Orders, and display the table of hits.

### ISM New Orders

```python

start_dates = ["2023-01-04", "2023-04-01", "2023-07-01", "2023-10-01"]
end_dates = ["2023-03-31", "2023-06-30", "2023-09-30", "2023-12-30"]
results = []

for i in range(0, len(start_dates)):
    _data = (
        obb.economy.calendar(provider="fmp", start_date=start_dates[i], end_date=end_dates[i])
        .model_dump()["results"]
    )
    results.extend(_data)
events = pd.DataFrame.from_records(results).set_index("date").sort_index()

events[events["event"].str.contains("ISM Manufacturing New Orders")]
```

| date                | country   | event                              |   actual |   previous |   consensus | importance   | currency   |   change |   change_percent |
|:--------------------|:----------|:-----------------------------------|---------:|-----------:|------------:|:-------------|:-----------|---------:|-----------------:|
| 2023-01-04 15:00:00 | US        | ISM Manufacturing New Orders (Dec) |     45.2 |       47.2 |         nan | Low          | USD        |     -2   |           -4.237 |
| 2023-02-01 15:00:00 | US        | ISM Manufacturing New Orders (Jan) |     42.5 |       45.1 |         nan | Low          | USD        |     -2.6 |           -5.765 |
| 2023-03-01 20:00:00 | US        | ISM Manufacturing New Orders (Feb) |     47   |       42.5 |         nan | Low          | USD        |      4.5 |           10.588 |
| 2023-04-03 18:00:00 | US        | ISM Manufacturing New Orders (Mar) |     44.3 |       47   |         nan | Low          | USD        |     -2.7 |           -5.745 |
| 2023-05-01 18:00:00 | US        | ISM Manufacturing New Orders (Apr) |     45.7 |       44.3 |         nan | Low          | USD        |      1.4 |            3.16  |
| 2023-06-01 14:00:00 | US        | ISM Manufacturing New Orders (May) |     42.6 |       45.7 |         nan | Low          | USD        |     -3.1 |           -6.783 |
| 2023-07-03 18:00:00 | US        | ISM Manufacturing New Orders (Jun) |     45.6 |       42.6 |         nan | Low          | USD        |      3   |            7.042 |
| 2023-08-01 18:00:00 | US        | ISM Manufacturing New Orders (Jul) |     47.3 |       45.6 |          44 | Low          | USD        |      1.7 |            3.728 |
| 2023-09-01 14:00:00 | US        | ISM Manufacturing New Orders (Aug) |     46.8 |       47.3 |         nan | Low          | USD        |     -0.5 |           -1.057 |
| 2023-10-02 14:00:00 | US        | ISM Manufacturing New Orders (Sep) |     49.2 |       46.8 |         nan | Low          | USD        |      2.4 |            5.128 |
| 2023-11-01 14:00:00 | US        | ISM Manufacturing New Orders (Oct) |     45.5 |       49.2 |         nan | Low          | USD        |     -3.7 |           -7.52  |
| 2023-12-01 15:00:00 | US        | ISM Manufacturing New Orders (Nov) |    nan   |       45.5 |         nan | Low          | USD        |    nan   |            0     |

## Earnings Calendar

The earnings calendar works in a similar way. For companies outside of the US, try the `openbb-fmp` provider.

```python
calendar = (
    obb.equity.calendar.earnings(
        provider="fmp",
        start_date="2023-11-20",
        end_date="2023-11-24"
    ).to_df()
)
```

This returned 1,234 results, but let's filter it down to those companies with analysts estimates, and display the top ten by EPS consensus.

```python
(
    calendar[calendar["eps_consensus"].notnull()
    & calendar["revenue_consensus"].notnull()]
    .sort_values(by="eps_consensus", ascending=False)
    .head(10)
)
```

| report_date   | symbol   |   eps_consensus |   actual_eps |   actual_revenue |   revenue_consensus | period_ending   | reporting_time   | updated_date   |
|:--------------|:---------|----------------:|-------------:|-----------------:|--------------------:|:----------------|:-----------------|:---------------|
| 2023-11-22    | CAP.SN   |          279.3  |          nan |              nan |         690955000000 | 2023-09-30      | bmo              | 2023-11-19     |
| 2023-11-20    | ABDP.L   |           56.4  |          nan |              nan |         106000000    | 2023-09-29      | bmo              | 2023-11-19     |
| 2023-11-23    | 4206.T   |           56.3  |          nan |              nan |         62200000    | 2023-09-30      | bmo              | 2023-11-19     |
| 2023-11-22    | DE       |            7.58 |          nan |              nan |         12909600000 | 2023-10-29      | bmo              | 2023-11-19     |
| 2023-11-21    | NVDA     |            3.34 |          nan |              nan |         15194600000 | 2023-10-29      | amc              | 2023-11-19     |
| 2023-11-21    | LOW      |            3.1  |          nan |              nan |         21059700000 | 2023-11-03      | bmo              | 2023-11-19     |
| 2023-11-20    | MOH.AT   |            2.48 |          nan |              nan |         3030480000 | 2023-09-30      | bmo              | 2023-11-19     |
| 2023-11-20    | SJM      |            2.47 |          nan |              nan |        1947800000  | 2023-10-30      | bmo              | 2023-11-19     |
| 2023-11-21    | BIDU     |            2.45 |          nan |              nan |         4735580000 | 2023-09-30      | bmo              | 2023-11-19     |
| 2023-11-21    | DKS      |            2.42 |          nan |              nan |        2948570000 | 2023-10-28      | bmo              | 2023-11-19     |

:::tip
EPS values are reported in the currency of the exchange listing price, direct comparisons are not viable across domiciles without a conversion factor.
:::

## Dividend Calendar

The dividend calendar uses start/end dates that reflect the ex-dividend date - the date when it begins trading without dividend rights. Aside from the notable dates, the information returned tells you only the amount paid. Calculating the yield requires more data.

:::note

- Nasdaq provides a field for 'annualized_amount', which makes it easier to calculate a dividend yield.

- The `openbb-nasdaq` provider has US-only data for this endpoint.

- The same markets covered by FMP's earnings calendar are included in their dividend calendar.
:::

### Calculate Dividend Yield

The ten highest-payments going ex-div between November 20-24 are shown below. With T+2 settlement, a purchase needs to occur two days prior to the record date for payment eligibility. The dividend yield is the current payment annualized as a percent of the asset's price.

```python
dividends = (
    obb.equity.calendar.dividend(
        provider="nasdaq",
         start_date="2023-11-20",
         end_date="2023-11-24",
    ).to_df()
    .drop_duplicates(subset="symbol")
    .sort_values("amount", ascending=False)
    .reset_index()
    .set_index("symbol")
    .head(10)
)

symbols = dividends.index.tolist()
prices = (
    obb.equity.price.quote(symbols, provider="fmp").to_df()
    .reset_index()
    .set_index("symbol")["price"]
)
dividends["price"] = prices

dividends["yield"] = (
    round((dividends["annualized_amount"]/dividends["price"])*100, 4)
)

(
    dividends[["record_date", "payment_date", "amount", "annualized_amount", "price", "yield"]]
    .sort_values("yield", ascending=False)
)
```

| symbol   | record_date   | payment_date   |   amount |   annualized_amount |   price |   yield |
|:---------|:--------------|:---------------|---------:|--------------------:|--------:|--------:|
| USOI     | 2023-11-21    | 2023-11-27     |   1.8588 |             16.134  |   75.73 | 21.3046 |
| ATCD     | 2023-11-21    | 2023-12-26     |  60.14   |             60.14   | 1235    |  4.8696 |
| GLDI     | 2023-11-21    | 2023-11-27     |   1.5153 |              4.8216 |  141.8  |  3.4003 |
| CHTM     | 2023-11-21    | 2023-12-26     |  59.62   |             59.62   | 1856.95 |  3.2106 |
| CMI      | 2023-11-24    | 2023-12-07     |   1.68   |              6.72   |  225.5  |  2.98   |
| KLIB     | 2023-11-24    | 2023-12-15     |   2.1    |              4.2    |  144    |  2.9167 |
| SNA      | 2023-11-21    | 2023-12-11     |   1.86   |              7.44   |  277.76 |  2.6786 |
| NOC      | 2023-11-27    | 2023-12-13     |   1.87   |              7.48   |  464.17 |  1.6115 |
| CBCYB    | 2023-11-24    | 2023-12-01     |   3.75   |              8      |  647    |  1.2365 |
| CBCY     | 2023-11-24    | 2023-12-01     |   3.75   |              8      |  660    |  1.2121 |

## IPO Calendar

The IPO calendar shows events based on their status - `["upcoming", "priced", "withdrawn"]` - and Intrinio provides a filter for the min/max dollar amount offered.

:::note
The data from both Intrinio and Nasdaq is US-only, both relying on the SEC for filing information.
:::

Use the `status` parameter to find announcements in different stages of the cycle.

### Upcoming

The initial public offerings that are confirmed to be coming to market are categorized as 'upcoming'. The number of companies going public at any given time will depend on market cycles.

```python
obb.equity.calendar.ipo(provider="nasdaq", status="upcoming").to_df()
```

| symbol   | name         |   offer_amount |   share_count | expected_price_date   | id            | exchange       | share_price   |
|:---------|:-------------|---------------:|--------------:|:----------------------|:--------------|:---------------|:--------------|
| DOCO     | Docola, Inc. |      8235004 |       1060870 | 2023-11-21            | 995278-107909 | NASDAQ Capital | 5.75-6.75     |

### Withdrawn

A `withdrawn` status might be the result of a SPAC unwinding after failing to merge with a company.

```python
obb.equity.calendar.ipo(provider="nasdaq", status="withdrawn").to_df().tail(3)
```

| withdraw_date   | name                      |   offer_amount |   share_count | filed_date   | id             |
|:----------------|:--------------------------|---------------:|--------------:|:-------------|:---------------|
| 2023-11-09      | Arago Acquisition Corp.   |      86250000.0 |       7500000 | 2022-05-06   | 1214792-102968 |
| 2023-11-13      | CW Petroleum Corp         |      17249995.5  |       3157894 | 2022-06-02   | 1055531-103241 |
| 2023-11-13      | Tiga Acquisition Corp. II |     230000000.0   |      20000000 | 2021-02-26   | 1148285-96307  |

### SPO

SPOs, secondary pubic offerings, are shares being sold by investors after an IPO. The money does not go to the company, but directly to the investor selling shares into the market. The `openbb-nasdaq` provider has an additional boolean parameter, `is_spo`. By default, year-to-date data is returned.

```python
obb.equity.calendar.ipo(provider="nasdaq", is_spo=True).to_df().tail(1)
```

| symbol   | ipo_date   | name                                    |   offer_amount |   share_count | deal_status   | id            | exchange             |   share_price |
|:---------|:-----------|:----------------------------------------|---------------:|--------------:|:--------------|:--------------|:---------------------|--------------:|
| SKWD     | 2023-11-16 | Skyward Specialty Insurance Group, Inc. |      152500000.0 |       5000000 | Priced        | 854131-108262 | NASDAQ Global Select |          30.5 |
