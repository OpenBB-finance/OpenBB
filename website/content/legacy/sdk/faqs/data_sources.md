---
title: Data and Sources
sidebar_position: 4
description: OpenBB is a data aggregator that provides access to data from various
  sources. It is important to understand how to load ticker symbols, end-of-day daily
  data, and handle certain limitations like accessing the Binance API. Feature request
  options are available for specific data source endpoints.
keywords:
- data aggregators
- data providers
- ticker symbols
- end-of-day daily data
- Binance API
- feature request
- live feeds
- load function
---

import HeadTitle from '@site/src/components/General/HeadTitle.tsx';

<HeadTitle title="Data and Sources - Faqs | OpenBB SDK Docs" />

Please note that OpenBB does not provide any data, it is an aggregator which provides users access to data from a variety of sources. OpenBB does not maintain or have any control over the raw data supplied. If there is a specific problem with the output from a data provider, please consider contacting them first.

<details><summary>Is there a list of all data providers?</summary>

The complete list is found [here](/terminal/usage/data/api-keys)

</details>

<details><summary>How do I load a ticker symbol from India?</summary>

Ticker symbols listed on exchanges outside of the US will have a suffix attached, for example, Rico Auto Industries Limited:

```console
df = openbb.stocks.load("ricoauto.ns")
```

The precise naming convention will differ by source, reference each source's own documentation for specific details.

</details>

<details><summary>Data from today is missing.</summary>

By default, the load function requests end-of-day daily data and is not included until the EOD summary has been published. The current day's data is considered intraday and is loaded when the `interval` argument is present.

```console
df = openbb.stocks.load(SPY, interval = 60)
```

</details>

<details><summary>Can I stream live prices and news feeds?</summary>

It is not currently possible to stream live feeds with the OpenBB SDK.

</details>

<details><summary>"Pair BTC/USDT not found in binance"</summary>

US-based users are currently unable to access the Binance API. Please try loading the pair from a different source, for example:

`load btc --source CCXT --exchange kraken`

</details>

<details><summary>How can I request adding endpoints from a specific data source?</summary>

Please [request a feature](https://openbb.co/request-a-feature) by submitting a new request.

</details>
