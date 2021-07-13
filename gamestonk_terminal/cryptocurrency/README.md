# CRYPTOCURRENCY

This menu aims to explore crypto world, and the usage of the following commands along with an example will be exploited below.

Note that we have added the ability to look at technical analysis in the ta menu.  Data loaded from CoinGecko has no candle data,
so indicators that rely on anything other than close will fail with an error.


* [finbrain](#finbrain)
    * crypto sentiment from 15+ major news headlines for more then 100 coins

[COINGECKO standalone menu](/gamestonk_terminal/cryptocurrency/coingecko/)

[COINMARKETCAP standalone menu](/gamestonk_terminal/cryptocurrency/coinmarketcap/)

[BINANCE standalone menu](/gamestonk_terminal/cryptocurrency/binance/)

[COINPAPRIKA standalone menu](/gamestonk_terminal/cryptocurrency/coinpaprika/)

## finbrain <a name="finbrain"></a>

```bash
usage: finbrain [-c --coin]
```

FinBrain collects the news headlines from 15+ major financial news sources on a daily basis and analyzes them to generate sentiment scores for more than 4500 US stocks. FinBrain Technologies develops deep learning algorithms for financial analysis and prediction, which currently serves traders from more than 150 countries all around the world. [Source: See https://finbrain.tech]

Currently all sentiment is gathered for  `COIN-USD` pairs. Please use upper case symbols of coins.

* -c/--coin - Symbol of the Coin for which you want to analyse sentiment. Currently available coins are:
```
AAVE, ADA, ADX, AE, ANT, ARDR, ARK, ATOM, BAT, BCCOIN, BCH, BCN, BLOCK, BNB, BNT, BTC, BTCD, BTG, BTM, BTS, CVC, DASH,
DCN, DCR, DGB, DGD, DNT, DOGE, DOT, EDG, EOS, ETH, ETP, FAIR, FCT, FUN, GAME, GAS, GBYTE, GNO, GNT, HSR, ICX, IOC, KIN,
KMD, KNC, LINK, LKK, LRC, LSK, LTC, MAID, MCAP, MCO, MGO, MKR, MLN, MONA, MTL, NAV, NEBL, NEO, NLC2, NXS, NXT, OMG, PAY,
PIVX, PPT, QASH, QRL, QTUM, REP, RLC, SALT, SC, SMART, SNGLS, STEEM, STORJ, SUB, SYS, TAAS, TRX, UBQ, UNI, USDT, VEN,
VERI, VTC, WAVES, WINGS, WTC, XCP, XLM, XMR, XRP, XTZ, XVG, YFI, ZEC, ZEN, ZRX
```

![image](https://user-images.githubusercontent.com/275820/125166701-126a3f00-e19d-11eb-9f81-26c844f7dd62.png)
