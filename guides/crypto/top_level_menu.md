---
title: Introduction to Cryptocurrency
keywords: "crypto, web3, nft, blockchain"
date: "2022-06-20"
type: our story
status: publish
excerpt: "The Introduction to Cryptocurrency explains how to use the Cryptocurrency and provides a brief description of its sub-menus"
---


# Introduction to Cryptocurrency
The Cryptocurrency menu allows you to discover trending cryptocurrency [(disc)](https://openbb-finance.github.io/OpenBBTerminal/terminal/crypto/disc/). Additionally, you can also perform research of a specific coin [(dd)](https://openbb-finance.github.io/OpenBBTerminal/terminal/crypto/dd/), NFT [(nft)](https://openbb-finance.github.io/OpenBBTerminal/terminal/crypto/nft/) or most lucrative Defi project [(defi)](https://openbb-finance.github.io/OpenBBTerminal/terminal/crypto/defi/). It does so by handing you tools to (among other things) to perform technical analysis [(ta)](https://openbb-finance.github.io/OpenBBTerminal/terminal/crypto/ta/), quantitative analysis [(qa)](https://openbb-finance.github.io/OpenBBTerminal/terminal/crypto/ta/), and give you access to onchain information [(onchain)](https://openbb-finance.github.io/OpenBBTerminal/terminal/crypto/onchain/).


## How to use
The Cryptocurrency menu is called upon by typing `crypto` which opens the following menu:

<img width="1317" alt="image" src="https://user-images.githubusercontent.com/40023817/174688140-3fb055ba-aaef-487c-b978-10a88c04e349.png">


You have the ability to search a coin with `find` based on its name or symbol. An example:

<img width="551" alt="image" src="https://user-images.githubusercontent.com/40023817/174688194-6d06b5fa-65c3-4c95-9c11-def35605fdbb.png">

As a result, you can see a list of coins matching your search criteria. Once you identify the coin you are looking for, next step is to `load` it. See the example below:

<img width="851" alt="image" src="https://user-images.githubusercontent.com/40023817/174688215-ae86ad39-a394-48c6-a6fc-bfd560296c89.png">


To view the candle chart for the loaded crypto, you can call `candle`. This will show you the coin's historical prices and volume, as follows:
<img width="786" alt="image" src="https://user-images.githubusercontent.com/40023817/174688395-cd201677-0f01-43d2-a22f-892ae63b25e2.png">

In case you want to adjust the default period, you can do so by specifying the number of days to go back in time.

<img width="886" alt="image" src="https://user-images.githubusercontent.com/40023817/174688639-306ddc43-b202-436b-bbc2-c1bd6376c857.png">

You might be wondering, how can I know about all possible options? You can type in `command_name -h` or `load -h` in this case. Here you will find available optional arguments that you can play with.

<img width="832" alt="image" src="https://user-images.githubusercontent.com/40023817/174688752-0e0286c6-ac78-42f8-8215-354bc951f182.png">


Lastly, by calling `?` or `help` or `h`, the `crypto` menu will be re-populated. Here you can see that several menus have turned blue, which mean you can enter any of them now. In order to use these menus, you are required to first `load` a coin.
<img width="1349" alt="image" src="https://user-images.githubusercontent.com/40023817/174688823-16fbd8b0-d9ee-47b0-a2c3-fd90b749fc32.png">


## Sub-menus available
The Cryptocurrency menu has an extensive list of available sub-menus ranging from due diligence to NFT to onchain analysis. To find more information about each menu, you can click on one of the following:

- [Introduction to Cryptocurrency Discovery](https://openbb-finance.github.io/OpenBBTerminal/terminal/cryptocurrency/discovery): discovers top trending, top gainers or losers coins, as well as top NFTs, dApps and exchanges based on prices.
- [Introduction to Overview](https://openbb-finance.github.io/OpenBBTerminal/terminal/cryptocurrency/overview/): gives the overview of the cryptocurrency market, including global Defi market, stablecoins, exchanges as well as latest news.
- [Introduction to Onchain](https://openbb-finance.github.io/OpenBBTerminal/terminal/cryptocurrency/onchain/): provides information on different blockchains, whales transaction and traded volumes on certain crypto pair. You can also specify a Ethereum address and look up past transactions and balance history.
- [Introduction to DeFi](https://openbb-finance.github.io/OpenBBTerminal/terminal/cryptocurrency/defi/): explore the decentralized finance market through a variety of indicators and data, from lending interests, staking ratio, Uniswap pools to top Defi dApps.
- [Introduction to Tools](https://openbb-finance.github.io/OpenBBTerminal/terminal/cryptocurrency/tools/): gives you the tool to calculate crypto metrics, such as impermanent loss and converting APR to APY.
- [Introduction to NFTs](https://openbb-finance.github.io/OpenBBTerminal/terminal/cryptocurrency/nft/): Discover latest NFT drops and OpenSea's NFT Collection statistics.
- [Introduction to Due Diligence](https://openbb-finance.github.io/OpenBBTerminal/terminal/cryptocurrency/due_diligence/): performs due diligence on a chosen coin based on, among other things, tokenomics, roadmaps, news, and community.
- [Introduction to Technical Analysis](https://openbb-finance.github.io/OpenBBTerminal/terminal/cryptocurrency/technical_analysis/): analyzes the chosen coin's historical data extensively with moving averages and momentum, trend, volatility and volume indicators.
- [Introduction to Prediction Techniques](https://openbb-finance.github.io/OpenBBTerminal/terminal/cryptocurrency/prediction_techniques/): applies advanced AI and Machine Learning models to form prediction of future stock prices including Recurrent Neural Network (RNN), Autoregressive Integrated Moving Average (ARIMA) and Monte Carlo forecasting

## Examples

When entering the `crypto` menu, you would typically want to load in a coin. Let's go with Ethereum. You can do this by specifying its symbol: `load eth`
![image](https://user-images.githubusercontent.com/40023817/175827660-3b106e6e-2638-4536-939e-e38692ec1003.png)


Let's checkout its sentiments from major headlines news by typing: `headlines`
<img width="791" alt="image" src="https://user-images.githubusercontent.com/40023817/175827670-15042c5e-0650-486e-92fa-a154de13b208.png">


To perform further analysis, the best menu to enter is `dd`.
<img width="791" alt="image" src="https://user-images.githubusercontent.com/40023817/175827687-5212030a-7871-4773-908f-b5ee0376c674.png">

We can checkout the project's roadmap and its effect to historical price, by typing `rm`

<img width="789" alt="image" src="https://user-images.githubusercontent.com/40023817/175827701-b6b01a67-b90a-4aac-94bf-b9f5a19023c5.png">


Once you have finished analyzing a specific coin, you would want to get a good understanding of the overall crypto market. To do that, head over to `ov` by typing `../ov`.
Hint: `..` basically took you back to the previous menu. Instead of performing 2 separate commands, you can combine them together using `/`. As such `../ov` will take us back to previous menu, and then enter the `ov` menu.

<img width="789" alt="image" src="https://user-images.githubusercontent.com/40023817/175827714-8545c2c4-88f3-4415-9e53-3c1938717c30.png">


Bitcoin has such a big influence on the entire crypto market. So seeing whether we are in a Bitcoin season or a Altcoin season will be useful to your investment decisions. `altindex` is a great command for this purpose.

<img width="786" alt="image" src="https://user-images.githubusercontent.com/40023817/175827720-323ea70c-6eab-4cc7-819c-9fe1339af380.png">
