---
title: Introduction
sidebar_position: 1
description: Documentation page detailing how to use the Cryptocurrency menu providing
  trending cryptocurrency insights, researching specific coins, as well as providing access to onchain information.
  Includes sub-menus for in-depth discovery, overview, onchain analysis, Defi, NFTs
  and due diligence. Examples provided for navigating through features.
keywords:
- Cryptocurrency
- NFT
- Defi
- technical analysis
- quantitative analysis
- onchain information
- cryptocurrency analysis
- coin research
- crypto market
- forecasts
- Decentralized Finance
- Non Fungible Tokens
- crypto due diligence
- Ethereum
- Bitcoin
- blockchain transactions
- OpenSea NFT
- crypto news sentiment
- crypto project roadmap
- crypto market overview
- Altcoin season
---

import HeadTitle from '@site/src/components/General/HeadTitle.tsx';

<HeadTitle title="Introduction - Crypto - Menus | OpenBB Terminal Docs" />

The Crypto menu has functions and sub-menus for the discovery and analysis of digtal assets.  Enter, from the main menu, by typing `crypto` into the Terminal.

![crypto](https://github.com/OpenBB-finance/OpenBBTerminal/assets/85772166/63ebe2a5-27c2-4ca5-bdfe-2c1d51dde69d)

## Usage

At the base of the menu, there are six functions. They are are displayed above, in light blue text.  Sub-menus are distinguished by a `>`, on the left side of the item.

- load
- find
- price
- headlines
- candle
- prt

### Load

The `load` command is similar to the `/stocks/load` command, with some key differences:

- `--vs` parameter is for relative pricing in a specific fiat or stable coin.
- When the `--source` is "CCXT", an `--exchange` parameter is required to select the specific data source.
  - Data availability and granularity varies.

![Screenshot 2023-10-30 at 3 40 43 PM](https://github.com/OpenBB-finance/OpenBBTerminal/assets/85772166/f3bf898a-366a-4344-8b37-5621f411774f)

```console
/crypto/load --vs usd -c btc --source CCXT --exchange bitfinex
```

vs.

```console
/crypto/load --vs usd -c btc --source CCXT --exchange binance
```

![Screenshot 2023-10-30 at 3 19 00 PM](https://github.com/OpenBB-finance/OpenBBTerminal/assets/85772166/c87e14ff-08b1-4c54-81ec-a310ce7a5590)

### Price

The `price` command displays realtime prices from Pyth.  This command will stay active until `ctrl-c` is entered, which breaks the connection.  A second instance of the Terminal could be started to keep a connection alive.

```console
/crpyto/price SOL-USD
```

![Screenshot 2023-10-30 at 3 36 22 PM](https://github.com/OpenBB-finance/OpenBBTerminal/assets/85772166/fd3315f8-4500-4534-8fcc-24a330cc2ccf)


## Sub-Menus

The Cryptocurrency menu has an extensive list of available sub-menus ranging from due diligence to NFT to onchain analysis. To find more information about each menu, you can click on one of the following:

- [Discovery](disc.md): Top trending, top gainers or losers coins, as well as top NFTs, dApps and exchanges based on prices.
- [Overview](ov.md): General overviews of the cryptocurrency market, including global Defi market, stablecoins, exchanges as well as latest news.
- [Onchain](onchain.md): Onchain data for the Ethereum-based assets. Look up addresses with past transactions and balance history.
- [DeFi](defi.md): DeFi networks and data.
- [NFTs](nft.md): Discover latest NFT drops and OpenSea's NFT Collection statistics.
- [Due Diligence](dd.md): Perform due diligence on a chosen coin or project with information such as, tokenomics, roadmaps, news, and community.

There are also entry points to Terminal toolkits:

- [Forecast](/terminal/menus/forecast.md): Forecast menu.
- [Quantitative Analysis](/terminal/menus/common/qa.md): Quantitative Analysis menu.
- [Technical Analysis](/terminal/menus/common/ta.md): Technical Analysis menu.
