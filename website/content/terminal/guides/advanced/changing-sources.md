---
sidebar_position: 2
title: Changing Sources
---

Many commands have multiple datasources attached to it. A great example is `/stocka/fa/income` that allows you to select `YahooFinance, Polygon, AlphaVantage, FinancialModelingPrep or EODHD`. Many have a default source, for example for `income` this is Yahoo Finance but you can change the default sources of each command via the `sources` menu.

```
2022 Nov 23, 06:09 (🦋) / $ sources

╭─────────────────────────────────────────────────────────────────────────────────────────────────── Data Sources ───────────────────────────────────────────────────────────────────────────────────────────────────╮
│                                                                                                                                                                                                                    │
│ Get and set default data sources:                                                                                                                                                                                  │
│     get                get available data sources associated with command                                                                                                                                          │
│     set                set default data source for a command                                                                                                                                                       │
│                                                                                                                                                                                                                    │
╰──────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────── OpenBB Terminal v2.0.0rc1 (https://openbb.co) ─╯
```

For example, if you would like to change the default data provider from the `income` command from the `stocks/fa` menu you can first run the command `get` following by `stocks_load`. This returns the following:

```
2022 Nov 23, 06:12 (🦋) /sources/ $ get stocks_fa_income


Default   : YahooFinance
Available : YahooFinance, Polygon, AlphaVantage, FinancialModelingPrep, EODHD

```

Then, with `set` you can change the default data provider. For example, we can change the data provider to `Polygon` with
the following:

```
2022 Nov 23, 06:12 (🦋) /sources/ $ set stocks_fa_income Polygon

The data source was specified successfully.


2022 Nov 23, 06:12 (🦋) /sources/ $ get stocks_fa_income


Default   : Polygon
Available : Polygon, YahooFinance, AlphaVantage, FinancialModelingPrep, EODHD

```
