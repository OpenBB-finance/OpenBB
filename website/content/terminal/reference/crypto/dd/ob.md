---
title: ob
description: This page explains how to retrieve the order book for any selected cryptocurrency
  coin across numerous exchanges. It specifically instructs the use of the 'ob' command
  in python.
keywords:
- order book
- cryptocurrency
- exchange
- quote currency
- cryptocurrency pairs
- binance
- bitfinex
- coinbase
- poloniex
- crypto trading
- trading parameters
---

import HeadTitle from '@site/src/components/General/HeadTitle.tsx';

<HeadTitle title="crypto /dd/ob - Reference | OpenBB Terminal Docs" />

Get the order book for selected coin

### Usage

```python wordwrap
ob [-e {ace,alpaca,ascendex,bequant,bigone,binance,binancecoinm,binanceus,binanceusdm,bingx,bit2c,bitbank,bitbay,bitbns,bitcoincom,bitfinex,bitfinex2,bitflyer,bitforex,bitget,bithumb,bitmart,bitmex,bitopro,bitpanda,bitrue,bitso,bitstamp,bitstamp1,bittrex,bitvavo,bkex,bl3p,blockchaincom,btcalpha,btcbox,btcmarkets,btctradeua,btcturk,bybit,cex,coinbase,coinbaseprime,coinbasepro,coincheck,coinex,coinfalcon,coinmate,coinone,coinsph,coinspot,cryptocom,currencycom,delta,deribit,digifinex,exmo,fmfwio,gate,gateio,gemini,hitbtc,hitbtc3,hollaex,huobi,huobijp,huobipro,idex,independentreserve,indodax,kraken,krakenfutures,kucoin,kucoinfutures,kuna,latoken,lbank,lbank2,luno,lykke,mercado,mexc,mexc3,ndax,novadax,oceanex,okcoin,okex,okex5,okx,paymium,phemex,poloniex,poloniexfutures,probit,tidex,timex,tokocrypto,upbit,wavesexchange,wazirx,whitebit,woo,yobit,zaif,zonda}] [--vs VS]
```

---

## Parameters

| Name | Parameter | Description | Default | Optional | Choices |
| ---- | --------- | ----------- | ------- | -------- | ------- |
| exchange | -e  --exchange | Exchange to search for order book | binance | True | ace, alpaca, ascendex, bequant, bigone, binance, binancecoinm, binanceus, binanceusdm, bingx, bit2c, bitbank, bitbay, bitbns, bitcoincom, bitfinex, bitfinex2, bitflyer, bitforex, bitget, bithumb, bitmart, bitmex, bitopro, bitpanda, bitrue, bitso, bitstamp, bitstamp1, bittrex, bitvavo, bkex, bl3p, blockchaincom, btcalpha, btcbox, btcmarkets, btctradeua, btcturk, bybit, cex, coinbase, coinbaseprime, coinbasepro, coincheck, coinex, coinfalcon, coinmate, coinone, coinsph, coinspot, cryptocom, currencycom, delta, deribit, digifinex, exmo, fmfwio, gate, gateio, gemini, hitbtc, hitbtc3, hollaex, huobi, huobijp, huobipro, idex, independentreserve, indodax, kraken, krakenfutures, kucoin, kucoinfutures, kuna, latoken, lbank, lbank2, luno, lykke, mercado, mexc, mexc3, ndax, novadax, oceanex, okcoin, okex, okex5, okx, paymium, phemex, poloniex, poloniexfutures, probit, tidex, timex, tokocrypto, upbit, wavesexchange, wazirx, whitebit, woo, yobit, zaif, zonda |
| vs | --vs | Quote currency (what to view coin vs) | usdt | True | AUD, BIDR, BKRW, BNB, BRL, BTC, BUSD, BVND, DAI, DOGE, DOT, ETH, EUR, GBP, IDRT, NGN, PAX, PLN, RUB, TRX, TRY, TUSD, UAH, USDC, USDP, USDS, USDT, UST, VAI, XRP, ZAR |

---
