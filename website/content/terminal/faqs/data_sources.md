---
title: Data and Sources
sidebar_position: 4
description: Information about data sources and providers offered through the OpenBB Terminal.
keywords:
  [
    installation,
    installer,
    install,
    guide,
    mac,
    windows,
    linux,
    python,
    github,
    macos,
    how to,
    explanation,
    openbb terminal,
    data,
    data provider,
    india,
    binance
  ]
---

import HeadTitle from '@site/src/components/General/HeadTitle.tsx';

<HeadTitle title="Data Sources - Terminal | OpenBB Docs" />

## Data and Sources

Please note that OpenBB does not provide any data, it is an aggregator which provides users access to data from a variety of sources. OpenBB does not maintain or have any control over the raw data supplied. If there is a specific problem with the output from a data provider, please consider contacting them first.

<details><summary>Is there a list of all data providers?</summary>

The complete list is found [here](https://docs.openbb.co/terminal/usage/guides/api-keys)

</details>

<details><summary>How do I find and load a ticker symbol from India, or any other country?</summary>

Use the [`/stocks/search`](https://docs.openbb.co/terminal/usage/intros/stocks#search) command.

```console
search --country canada --industrygroup banks
```

Ticker symbols listed on exchanges outside of the US will have a suffix attached, for example, Rico Auto Industries Limited:

```console
load ricoauto.ns
```

The precise naming convention will differ by source, reference each source's own documentation for specific details.

</details>

<details><summary>Data from today is missing.</summary>

By default, the load function requests end-of-day daily data and is not included until the EOD summary has been published. The current day's data is considered intraday and is loaded when the `interval` argument is present.

```console
load SPY -i 60
```

</details>

<details><summary>Can I stream live prices and news feeds?</summary>

The OpenBB Terminal is not currently capable of streaming live feeds through websocket connections.

</details>

<details><summary>"Pair BTC/USDT not found in binance"</summary>

US-based users are currently unable to access the Binance API. Please try loading the pair from a different source, for example:

`load btc --source CCXT --exchange kraken`

</details>

<details><summary>How can I request functionality for a specific data source?</summary>

Please [request a feature](https://openbb.co/request-a-feature) by submitting a new request.

</details>
