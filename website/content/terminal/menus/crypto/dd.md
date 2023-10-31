---
title: Due Diligence
description: Guide to the Cryptocurrency Due Diligence menu command in the crypto
  terminal. It offers information about the loaded coin, project details, the token
  balance, fundraising details and social media activity. Examples of usage, price
  movements and sentiment scores are provided. The guide provides detailed step-by-step
  instructions on how to use all the features of the Cryptocurrency Due Diligence
  command.
keywords:
- Cryptocurrency Due Diligence
- crypto
- load
- Coin
- coin metrics
- trades
- coin information
- project information
- Muir Glacier
- Istanbul
- sentiment analysis
- scores
---

import HeadTitle from '@site/src/components/General/HeadTitle.tsx';

<HeadTitle title="Due Diligence - Crypto - Menus | OpenBB Terminal Docs" />

The Due Diligence sub-menu provides a layer of tools for researching a digital asset, from a bottom-up perspective, with functions for tokenomics, community engagement, governance, roadmaps, whitepapers, and more.  The commands are grouped into sections:

- Overview
- Market
- Metrics
- Contributors and Investors
- Tokenomics
- Roadmap and News
- Activity and Community

:::note

Functions in this menu do not rely on the selected `--source` from the `load` command.  The source of data for each command is located on the far-right of the menu item, in square brackets. 

:::

## Usage

Switch the current asset with the `load` command.  A coin does not have to be loaded before entering the menu.

```console
load xrp
```

### PI

The `pi` command obtains key project information from Messari.

```console
/crypto/dd/load xrp/pi
```

In this instance, there are no data points for audits or vulnerabilities.

```console
Audits not found

Vulnerabilities not found
```

A description of the project and technology is returned in a table:

![project information](https://github.com/OpenBB-finance/OpenBBTerminal/assets/85772166/5ccc696d-4af6-41f8-9386-b621334f23a6)

### PS

Similar to `pi`, `ps` are key statitistics of the asset from Messari.

```console
/crypto/dd/load xrp/ps
```

| name                       | XRP                 |
|:---------------------------|:--------------------|
| id                         | xrp-xrp             |
| symbol                     | XRP                 |
| rank                       | 5                   |
| circulating_supply         | 53560508378         |
| total_supply               | 99988331658         |
| max_supply                 | 100000000000        |
| beta_value                 | 1.018               |
| first_data_at              | 2013-08-04 00:00:00 |
| last_updated               | 2023-10-31 02:56:18 |
| usd_price                  | 0.5766098562100087  |
| usd_volume_24h             | 1270078728.0050828  |
| usd_volume_24h_change_24h  | 130.86              |
| usd_market_cap             | 30883517034         |
| usd_market_cap_change_24h  | 3.76                |
| usd_percent_change_15m     | -0.23               |
| usd_percent_change_30m     | -0.45               |
| usd_percent_change_1h      | -0.63               |
| usd_percent_change_6h      | -0.66               |
| usd_percent_change_12h     | -0.83               |
| usd_percent_change_24h     | 3.76                |
| usd_percent_change_7d      | 5.21                |
| usd_percent_change_30d     | 10.77               |
| usd_percent_change_1y      | 26.09               |
| usd_ath_price              | 3.84194             |
| usd_ath_date               | 2018-01-04 07:14:00 |
| usd_percent_from_price_ath | -84.99              |


### Trades

The `trades` command requests data via CCXT, pick the venue to see the latest trades.

![Screenshot 2023-10-30 at 8 11 05 PM](https://github.com/OpenBB-finance/OpenBBTerminal/assets/85772166/2ae64595-d78d-48c4-b12f-75e929d0b6d2)

```console
/crypto/dd/load xrp/trades kraken
```

![Screenshot 2023-10-30 at 8 09 34 PM](https://github.com/OpenBB-finance/OpenBBTerminal/assets/85772166/1e66e39b-3208-4be3-8e11-89d233de3770)


### OB

The order book, `ob`, from the same venue:

```console
/crypto/dd/load xrp/ob kraken
```

![Screenshot 2023-10-30 at 8 14 02 PM](https://github.com/OpenBB-finance/OpenBBTerminal/assets/85772166/28846e0b-e3fa-4828-bc12-493a632c5917)


### Inv

The investors function, `inv`, shows who is backing the project. 

```console
/crypto/dd/load xrp/inv
```

![Screenshot 2023-10-30 at 8 20 03 PM](https://github.com/OpenBB-finance/OpenBBTerminal/assets/85772166/f0eabb1c-334c-44a4-9ef1-72f2c6799be1)
