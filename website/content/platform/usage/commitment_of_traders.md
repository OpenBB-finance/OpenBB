---
title: Commitment of Traders
sidebar_position: 7
description: This page provides details on the accessing Commitment of Traders reports with
  the OpenBB Platform, published by the CFTC weekly.  This guide provides examples for
  using the combinations of parameters used to get aspects of the report's data.
keywords:
- futures
- commodities
- index
- indices
- positioning
- dealer
- hedge
- open interest
- Nasdaq DataLink
- CFTC
- commitment of traders
- COT
- Treasury Note
- currency
- currencies
- equity
---

import HeadTitle from '@site/src/components/General/HeadTitle.tsx';

<HeadTitle title="Commitment of Traders - Usage | OpenBB Platform Docs" />

Commitment of Traders (COT) reports are published on Fridays, by the [CFTC](https://www.cftc.gov/MarketReports/CommitmentsofTraders/index.htm). CFTC COT reports provide a breakdown of each Tuesday’s open interest for futures and options on futures markets in which 20 or more traders hold positions equal to or above the reporting levels established by the CFTC.

## Regulators Module

The `obb.regulators` module contains data published by industry regulators and agencies. The data will not be specific to any particular asset class, and the information is available to the general public. The COT reports have two end points:

- `obb.regulators.cftc.cot()`
- `obb.regulators.cfc.cot_search()`

While the data is public and available directly from the CFTC website, [Nasdaq Data Link](https://data.nasdaq.com/databases/CFTC) provides access to a parsed database with the complete history, of current and obsolete reports, that the `openbb-nasdaq` data provider connects to.

### COT Search

The `obb.regulators.cftc.cot_search()` end point is a curated list of the 100 most common reports. The list can be searched by fuzzy query - i.e., "commodities" - and they are classified under categories and subcategories. Get the whole list with an empty query.

```python
reports = obb.regulators.cftc.cot_search().to_df()
```

The major US indices - S&P 500, Nasdaq 100, Dow Jones Industrial Average, Russell 1000 & 2000, VIX, Bloomberg Commodity Index, etc. - are categorized as "Index".

```python
reports[reports["category"] == "Index"]
```

### COT Reports

There is a default report, Two-Year Treasury Note Futures, which has the code: `042601`. Where available, like the two-year note, the futures continuation symbol (ZT=F) can be used instead of the code. The name can also be used:

```python
zt = obb.regulators.cftc.cot("Two-Year Treasury Note Futures (CBT)").to_df()

zt.iloc[-1]
```

|                               |   2023-11-14 |
|:------------------------------|----------------:|
| open_interest                 |           4274379 |
| noncommercial_long            |      427897           |
| noncommercial_short           |           1827558 |
| noncommercial_spreads         |      121573           |
| commercial_long               |           3456965 |
| commercial_short              |           2188950 |
| total_long                    |           4006435 |
| total_short                   |          4138081  |
| nonreportable_positions_long  |      267944           |
| nonreportable_positions_short |      136297           |

:::note
Look up reports not listed under `obb.regulators.cftc.cot_search()` by using the Nasdaq Data Link code for the series. Refer to their documentation for a complete list.
:::

### Parameters

There are parameters that will alter the type of report returned.

:::note
Not every combination of parameters is valid for all reports. An error will be raised when parameters are invalid.
:::

#### `data_type`

The `data_type` changes what is returned, futures or futures and options.

- `F` (futures only)

- `FO` (futures and options)

- `CITS` (Commodity Index Trader Supplemental - only valid for commodities.)

The Supplemental report includes 13 select agricultural commodity contracts for combined futures and options positions. Supplemental reports break down the reportable open interest positions into three trader classifications:

- Non-Commercial
- Commercial
- Index Traders

The example below is the CITS report for corn futures.

```python
zc_cits =  obb.regulators.cftc.cot("ZC=F", data_type="CITS").to_df()

zc_cits.iloc[-1]
```

|                                        |   2023-11-14 |
|:---------------------------------------|----------------------:|
| open_interest_all                            |            1837197 |
| noncommercial_positions_long_all_no_cit      |      125917           |
| noncommercial_positions_short_all_no_cit     |      322629           |
| noncommercial_positions_spreading_all_no_cit |      564330           |
| commercial_positions_long_all_no_cit         |      591691           |
| commercial_positions_short_all_no_cit        |      602447           |
| total_reportable_positions_long_all          |           1635294 |
| total_reportable_positions_short_all         |           1612623 |
| nonreportable_positions_long_all             |      201904           |
| nonreportable_positions_short_all            |      224575           |
| positions_long_cit                           |      353355           |
| positions_short_cit                          |      123216           |

#### `legacy_format`

When `True`, reports are broken down by exchange. These reports have a futures only report and a combined futures and options report. Legacy reports break down the reportable open interest positions into two classifications: non-commercial and commercial traders.

```python
legacy_zt = obb.regulators.cftc.cot("ZT=F", legacy_format=True).to_df()

legacy_zt.iloc[-1]
```

|                          |   2023-11-14 |
|:-------------------|----------------:|
| open_interest            |           4274379 |
| dealer_longs             |      138114           |
| dealer_shorts            |      367211           |
| dealer_spreads           |       37152           |
| asset_manager_longs      |           1893280 |
| asset_manager_shorts     |      504752           |
| asset_manager_spreads    |      297009           |
| leveraged_funds_longs    |      968702           |
| leveraged_funds_shorts   |           2595004   |
| leveraged_funds_spreads  |      133108           |
| other_reportable_longs   |      507457           |
| other_reportable_shorts  |      172232           |
| other_reportable_spreads |       31614           |
| total_reportable_longs   |           4006435 |
| total_reportable_shorts  |           4138081 |
| non_reportable_longs     |      267944           |
| non_reportable_shorts    |      136298           |

#### `report_type`

The `report_type` parameter has four choices:

- `ALL`
- `CHG` (change in positions)
- `OLD`(old crop years)
- `OTR` (other crop years)

For selected commodities where there is a well-defined marketing season or crop year, the COT data are broken down by "old" and "other" crop years. The "Major Markets for Which the COT Data Is Shown by Crop Year" table (shown below) lists those commodities and the first and last futures of the marketing season or crop year. In order not to disclose positions in a single future near its expiration, on the first business day of the month of the last future in an "old" crop year, the data for that last future is combined with the data for the next crop year and is shown as "old" crop futures. An example is CBOT wheat, where the first month of the crop year is July and the last month of the prior crop year is May. On May 3, 2004, positions in the May 2004 futures month were aggregated with positions in the July 2004 through May 2005 futures months and shown as "old" crop futures. Positions in all subsequent wheat futures months were shown as "other."

For the "old" and "other" figures, spreading is calculated for equal long and short positions within a crop year. If a non-commercial trader holds a long position in an "old" crop-year future and an equal short position in an "other" crop-year future, the long position will be classified as "long-only" in the "old" crop year and the short position will be classified as "short-only" in the "other" crop year. In this example, in the "all" category, which considers each trader's positions without regard to crop year, that trader's positions will be classified as "spreading." For this reason, summing the "old" and "other" figures for long-only, for short-only, or for spreading will not necessarily equal the corresponding figure shown for "all" futures. Any differences result from traders that spread from an "old" crop-year future to an "other" crop-year future.

#### Major Markets for Which the COT Data Is Shown by Crop Year

|Market| Commodity | First Future| Last Future|
|:-------|:---------:|:-----:|-----:|
|CBOT| Wheat| 	July 	|May|
|CBOT| Corn| 	December |	September|
|CBOT| Oats |	July 	| May|
|CBOT| Soybeans |	September |August|
|CBOT| Soybean Oil |	October |	September|
|CBOT| Soybean Meal |	October |	September|
|CBOT| Rough Rice| 	September |	July|
|KCBT| Wheat |	July| 	May|
|MGE| Wheat |	September 	|July|
|CME| Lean Hogs |	December 	|October|
|CME| Frozen Pork Bellies |	February| 	August|
|NYBT| Cocoa |	December 	|September|
|NYBT| Coffee C |	December |	September|
|NYBT| Cotton No.2 |	October | July|
|NYBT| Frozen Conc Orange Juice |	January |	November|

#### `measure`

The `measure` parameter has four choices, with `None` as the default state.

- `CR` (concentration ratios)
- `NT` (number of traders)
- `OI` (percent of open interest)
- `CHG` (change in positions - only valid for when `data_type` is 'CITS')

The report shows the percents of open interest held by the largest four and eight reportable traders, without regard to whether they are classified as commercial or non-commercial. The concentration ratios are shown with trader positions computed on a gross long and gross short basis and on a net long or net short basis. The "Net Position" ratios are computed after offsetting each trader’s equal long and short positions. A reportable trader with relatively large, balanced long and short positions in a single market, therefore, may be among the four and eight largest traders in both the gross long and gross short categories, but will probably not be included among the four and eight largest traders on a net basis.

Based on the information contained in the report of futures-and-options combined in the short format, the Supplemental report shows an additional category of “Index Traders” in selected agricultural markets. These traders are drawn from the noncommercial and commercial categories. The noncommercial category includes positions of managed funds, pension funds, and other investors that are generally seeking exposure to a broad index of commodity prices as an asset class in an unleveraged and passively-managed manner. The commercial category includes positions for entities whose trading predominantly reflects hedging of over-the-counter transactions involving commodity indices—for example, a swap dealer holding long futures positions to hedge a short commodity index exposure opposite institutional traders, such as pension funds.

All of these traders—whether coming from the noncommercial or commercial categories—are generally replicating a commodity index by establishing long futures positions in the component markets and then rolling those positions forward from future to future using a fixed methodology. Some traders assigned to the Index Traders category are engaged in other futures activity that could not be disaggregated. As a result, the Index Traders category, which is typically made up of traders with long-only futures positions replicating an index, will include some long and short positions where traders have multi-dimensional trading activities, the preponderance of which is index trading. Likewise, the Index Traders category will not include some traders who are engaged in index trading, but for whom it does not represent a substantial part of their overall trading activity.

#### `transform`

The `transform` parameter modifies the requested report to show the values as the week-over-week difference, rate of change, cumulative, or normalized.  These are standard parameters for all Nasdaq Data Link queries.

- `diff`
- `rdiff`
- `cumul`
- `normalize`

:::info
Explanations in this page are from the explanatory notes on the CFTC's [website](https://www.cftc.gov/MarketReports/CommitmentsofTraders/ExplanatoryNotes/index.htm)
:::
