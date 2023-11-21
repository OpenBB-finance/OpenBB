---
title: load
description: A detailed guide on how to load any cryptocurrency to perform various
  analyses. This page includes the method to select an exchange and designate a particular
  interval along with explaining several parameters including start and end dates.
keywords:
- load
- crypto currency
- analysis
- Yahoo Finance
- ccxt
- cg
- source
- exchange
- interval
- parameters
- coin
- start
- end
- vs
---

import HeadTitle from '@site/src/components/General/HeadTitle.tsx';

<HeadTitle title="forex /qa/load - Reference | OpenBB Terminal Docs" />

Load crypto currency to perform analysis on. Yahoo Finance is used as default source. Other sources can be used such as 'ccxt' or 'cg' with --source. If you select 'ccxt', you can then select any exchange with --exchange. You can also select a specific interval with --interval.

### Usage

```python wordwrap
load [-c COIN] [-s START] [--exchange {ace,alpaca,ascendex,bequant,bigone,binance,binancecoinm,binanceus,binanceusdm,bingx,bit2c,bitbank,bitbay,bitcoincom,bitfinex,bitfinex2,bitflyer,bitforex,bitget,bithumb,bitmart,bitmex,bitopro,bitpanda,bitrue,bitso,bitstamp,bitstamp1,bittrex,bitvavo,bkex,bl3p,btcalpha,btcbox,btcmarkets,btctradeua,btcturk,bybit,cex,coinbase,coinbaseprime,coinbasepro,coincheck,coinex,coinfalcon,coinmate,coinone,coinsph,coinspot,cryptocom,currencycom,delta,deribit,digifinex,exmo,fmfwio,gate,gateio,gemini,hitbtc,hitbtc3,hollaex,huobi,huobijp,huobipro,idex,independentreserve,indodax,kraken,krakenfutures,kucoin,kucoinfutures,kuna,latoken,lbank,lbank2,lykke,mercado,mexc,mexc3,ndax,novadax,oceanex,okcoin,okex,okex5,okx,paymium,phemex,poloniex,poloniexfutures,probit,tidex,timex,tokocrypto,upbit,wavesexchange,wazirx,whitebit,woo,yobit,zaif,zonda}] [-e END] [-i {1,5,15,30,60,240,1440,10080,43200}] [--vs VS]
```

---

## Parameters

| Name | Parameter | Description | Default | Optional | Choices |
| ---- | --------- | ----------- | ------- | -------- | ------- |
| coin | -c  --coin | Coin to get. Must be coin symbol (e.g., btc, eth) | None | True | None |
| start | -s  --start | The starting date (format YYYY-MM-DD) of the crypto | 2020-11-16 | True | None |
| exchange | --exchange | Exchange to search | binance | True | ace, alpaca, ascendex, bequant, bigone, binance, binancecoinm, binanceus, binanceusdm, bingx, bit2c, bitbank, bitbay, bitcoincom, bitfinex, bitfinex2, bitflyer, bitforex, bitget, bithumb, bitmart, bitmex, bitopro, bitpanda, bitrue, bitso, bitstamp, bitstamp1, bittrex, bitvavo, bkex, bl3p, btcalpha, btcbox, btcmarkets, btctradeua, btcturk, bybit, cex, coinbase, coinbaseprime, coinbasepro, coincheck, coinex, coinfalcon, coinmate, coinone, coinsph, coinspot, cryptocom, currencycom, delta, deribit, digifinex, exmo, fmfwio, gate, gateio, gemini, hitbtc, hitbtc3, hollaex, huobi, huobijp, huobipro, idex, independentreserve, indodax, kraken, krakenfutures, kucoin, kucoinfutures, kuna, latoken, lbank, lbank2, lykke, mercado, mexc, mexc3, ndax, novadax, oceanex, okcoin, okex, okex5, okx, paymium, phemex, poloniex, poloniexfutures, probit, tidex, timex, tokocrypto, upbit, wavesexchange, wazirx, whitebit, woo, yobit, zaif, zonda |
| end | -e  --end | The ending date (format YYYY-MM-DD) of the crypto | 2023-11-21 | True | None |
| interval | -i  --interval | The interval of the crypto | 1440 | True | 1, 5, 15, 30, 60, 240, 1440, 10080, 43200 |
| vs | --vs | Quote currency (what to view coin vs). e.g., usdc, usdt, ... if source is ccxt, usd, eur, ... otherwise | usdt | True | None |

---
