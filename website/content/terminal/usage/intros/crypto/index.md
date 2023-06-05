---
title: Cryptocurrency
keywords: [crypto, web3, nft, blockchain, cryptocurrency, how to, example, sub-menu, menu]
description: The Introduction to Cryptocurrency explains how to use the Cryptocurrency menu and provides a brief description of its sub-menus such as due diligence, DeFi, discovery, NFTs, and Onchain.
---

import HeadTitle from '@site/src/components/General/HeadTitle.tsx';

<HeadTitle title="Cryptocurrency - Terminal | OpenBB Docs" />

The Cryptocurrency menu allows you to discover trending cryptocurrency (<a href="/terminal/usage/intros/crypto/disc/" target="_blank" rel="noreferrer noopener">disc</a>). Additionally, you can also perform research of a specific coin (<a href="/terminal/usage/intros/crypto/dd" target="_blank" rel="noreferrer noopener">dd</a>),
NFT (<a href="/terminal/usage/intros/crypto/nft" target="_blank" rel="noreferrer noopener">nft</a>) or most lucrative Defi project
(<a href="/terminal/usage/intros/crypto/defi" target="_blank" rel="noreferrer noopener">defi</a>). It does so by handing you tools to (among other things) perform technical analysis (<a href="/terminal/usage/intros/common/ta/" target="_blank" rel="noreferrer noopener">ta</a>), quantitative analysis (<a href="/terminal/usage/intros/common/qa" target="_blank" rel="noreferrer noopener">qa</a>), and give you access to onchain information (<a href="/terminal/usage/intros/crypto/onchain/" target="_blank" rel="noreferrer noopener">onchain</a>).

### How to use

The Cryptocurrency menu is called upon by typing `crypto` which opens the following menu:

<img width="800" alt="image" src="https://user-images.githubusercontent.com/46355364/218994185-0afe6b70-df8a-4ed3-a26a-0de4da834c7e.png"></img>

You have the ability to search a coin with `find` based on its name or symbol. An example:

```
(🦋) /crypto/ $ find btc

                           Similar Coins
┏━━━━━━━┳━━━━━━━━┳━━━━━━━━━━━━━━━━━━━━━━━━┳━━━━━━━━━━━━━━━━━━━━━━━━┓
┃ index ┃ symbol ┃ id                     ┃ name                   ┃
┡━━━━━━━╇━━━━━━━━╇━━━━━━━━━━━━━━━━━━━━━━━━╇━━━━━━━━━━━━━━━━━━━━━━━━┩
│ 0     │ btc    │ bitcoin                │ Bitcoin                │
├───────┼────────┼────────────────────────┼────────────────────────┤
│ 1     │ xbtc   │ wrapped-bitcoin-stacks │ Wrapped Bitcoin-Stacks │
├───────┼────────┼────────────────────────┼────────────────────────┤
│ 2     │ wbtc   │ wrapped-bitcoin        │ Wrapped Bitcoin        │
├───────┼────────┼────────────────────────┼────────────────────────┤
│ 3     │ vbtc   │ venus-btc              │ Venus BTC              │
├───────┼────────┼────────────────────────┼────────────────────────┤
│ 4     │ tbtc   │ t-bitcoin              │ τBitcoin               │
├───────┼────────┼────────────────────────┼────────────────────────┤
│ 4     │ tbtc   │ tbtc                   │ tBTC                   │
├───────┼────────┼────────────────────────┼────────────────────────┤
│ 5     │ tbtc   │ t-bitcoin              │ τBitcoin               │
├───────┼────────┼────────────────────────┼────────────────────────┤
│ 5     │ tbtc   │ tbtc                   │ tBTC                   │
├───────┼────────┼────────────────────────┼────────────────────────┤
│ 6     │ sbtc   │ sbtc                   │ sBTC                   │
├───────┼────────┼────────────────────────┼────────────────────────┤
│ 6     │ sbtc   │ siambitcoin            │ SiamBitcoin            │
├───────┼────────┼────────────────────────┼────────────────────────┤
│ 7     │ sbtc   │ sbtc                   │ sBTC                   │
├───────┼────────┼────────────────────────┼────────────────────────┤
│ 7     │ sbtc   │ siambitcoin            │ SiamBitcoin            │
├───────┼────────┼────────────────────────┼────────────────────────┤
│ 8     │ rbtc   │ rootstock              │ Rootstock RSK          │
├───────┼────────┼────────────────────────┼────────────────────────┤
│ 9     │ pbtc   │ ptokens-btc            │ pTokens BTC [OLD]      │
├───────┼────────┼────────────────────────┼────────────────────────┤
│ 9     │ pbtc   │ ptokens-btc-2          │ pTokens BTC            │
└───────┴────────┴────────────────────────┴────────────────────────┘
```

As a result, you can see a list of coins matching your search criteria. Once you identify the coin you are looking for, next step is to `load` it. See the example below:

```
(🦋) /crypto/ $ load BTC

                                                   BTC/USD Performance
┏━━━━━━━━━━━━━┳━━━━━━━━┳━━━━━━━━━┳━━━━━━━━┳━━━━━━━━━━┳━━━━━━━━━┳━━━━━━━━━━━━━━━━━┳━━━━━━━━━━━━━━━━━┳━━━━━━━━━━━━━━━━━━━━┓
┃             ┃        ┃         ┃        ┃          ┃         ┃                 ┃                 ┃                    ┃
┃ Price (USD) ┃ 1D     ┃ 7D      ┃ 1M     ┃ 1Y       ┃ YTD     ┃ Volatility (1Y) ┃ Volume (7D avg) ┃ Circulating Supply ┃
┡━━━━━━━━━━━━━╇━━━━━━━━╇━━━━━━━━━╇━━━━━━━━╇━━━━━━━━━━╇━━━━━━━━━╇━━━━━━━━━━━━━━━━━╇━━━━━━━━━━━━━━━━━╇━━━━━━━━━━━━━━━━━━━━┩
│ 22220.80    │ 1.99 % │ -4.49 % │ 6.42 % │ -47.82 % │ 33.15 % │ 62.15 %         │ 24.32 B         │ 19.291 M           │
└─────────────┴────────┴─────────┴────────┴──────────┴─────────┴─────────────────┴─────────────────┴────────────────────┘
```

To view the candle chart for the loaded crypto, you can call `candle`. This will show you the coin's historical prices and volume, as follows:

<img width="800" alt="image" src="https://user-images.githubusercontent.com/40023817/174688395-cd201677-0f01-43d2-a22f-892ae63b25e2.png"></img>

### Sub-menus available

The Cryptocurrency menu has an extensive list of available sub-menus ranging from due diligence to NFT to onchain analysis. To find more information about each menu, you can click on one of the following:

- [Introduction to Cryptocurrency Discovery](/terminal/usage/intros/crypto/disc): discovers top trending, top gainers or losers coins, as well as top NFTs, dApps and exchanges based on prices.
- [Introduction to Cryptocurrency Overview](/terminal/usage/intros/crypto/ov/): gives the overview of the cryptocurrency market, including global Defi market, stablecoins, exchanges as well as latest news.
- [Introduction to Cryptocurrency Onchain](/terminal/usage/intros/crypto/onchain/): provides information on different blockchains, whales transaction and traded volumes on certain crypto pair. You can also specify a Ethereum address and look up past transactions and balance history.
- [Introduction to Cryptocurrency Decentralized Finance (DeFi)](/terminal/usage/intros/crypto/defi/): explore the decentralized finance market through a variety of indicators and data, from lending interests, staking ratio, Uniswap pools to top Defi dApps.
- [Introduction to Non Fungible Tokens (NFTs)](/terminal/usage/intros/crypto/nft/): Discover latest NFT drops and OpenSea's NFT Collection statistics.
- [Introduction to Cryptocurrency Due Diligence](/terminal/usage/intros/crypto/dd/): performs due diligence on a chosen coin based on, among other things, tokenomics, roadmaps, news, and community.
- [Introduction to Technical Analysis](/terminal/usage/intros/common/ta/): analyzes the chosen coin's historical data extensively with moving averages and momentum, trend, volatility and volume indicators.
- [Introduction to Forecasting Menu](/terminal/usage/intros/forecast/): applies advanced AI and Machine Learning models to form prediction of future stock prices including Recurrent Neural Network (RNN), Autoregressive Integrated Moving Average (ARIMA) and Monte Carlo forecasting

### Examples

When entering the `crypto` menu, you would typically want to load in a coin. Let's go with Ethereum. You can do this by specifying its symbol: `load eth`

```
(🦋) /crypto/ $ load eth

                                                   ETH/USD Performance
┏━━━━━━━━━━━━━┳━━━━━━━━┳━━━━━━━━━┳━━━━━━━━┳━━━━━━━━━━┳━━━━━━━━━┳━━━━━━━━━━━━━━━━━┳━━━━━━━━━━━━━━━━━┳━━━━━━━━━━━━━━━━━━━━┓
┃             ┃        ┃         ┃        ┃          ┃         ┃                 ┃                 ┃                    ┃
┃ Price (USD) ┃ 1D     ┃ 7D      ┃ 1M     ┃ 1Y       ┃ YTD     ┃ Volatility (1Y) ┃ Volume (7D avg) ┃ Circulating Supply ┃
┡━━━━━━━━━━━━━╇━━━━━━━━╇━━━━━━━━━╇━━━━━━━━╇━━━━━━━━━━╇━━━━━━━━━╇━━━━━━━━━━━━━━━━━╇━━━━━━━━━━━━━━━━━╇━━━━━━━━━━━━━━━━━━━━┩
│ 1556.88     │ 2.76 % │ -6.89 % │ 0.28 % │ -46.93 % │ 28.17 % │ 83.45 %         │ 7.44 B          │ 120.500 M          │
└─────────────┴────────┴─────────┴────────┴──────────┴─────────┴─────────────────┴─────────────────┴────────────────────┘

```

Let's checkout its sentiments from major headlines news by typing: `headlines`

<img width="800" alt="image" src="https://user-images.githubusercontent.com/40023817/175827670-15042c5e-0650-486e-92fa-a154de13b208.png"></img>

To perform further analysis, the best menu to enter is `dd`. We can check out the project's roadmap and its effect to historical price, by typing `rm`

<img width="800" alt="image" src="https://user-images.githubusercontent.com/40023817/175827701-b6b01a67-b90a-4aac-94bf-b9f5a19023c5.png"></img>

Once you have finished analyzing a specific coin, you would want to get a good understanding of the overall crypto market. To do that, head over to `ov` by typing `../ov`.

> **Hint:** `..` basically took you back to the previous menu. Instead of
> performing 2 separate commands, you can combine them together using `/`. As
> such `../ov` will take us back to previous menu, and then enter the `ov` menu.

<img width="800" alt="image" src="https://user-images.githubusercontent.com/40023817/175827714-8545c2c4-88f3-4415-9e53-3c1938717c30.png"></img>

Bitcoin has such a big influence on the entire crypto market. So seeing whether we are in a Bitcoin season or a Altcoin season will be useful to your investment decisions. `altindex` is a great command for this purpose.

<img width="800" alt="image" src="https://user-images.githubusercontent.com/40023817/175827720-323ea70c-6eab-4cc7-819c-9fe1339af380.png"></img>
