---
title: trades
description: This page provides a comprehensive guide on how to get the latest trades
  for a selected coin, demonstrating usage in Python. It explains the parameters required
  and supports a variety of exchanges, including Binance and Bitfinex.
keywords:
- trades
- cryptocurrency
- coin
- exchange
- parameters
- quote currency
- bitfinex
- binance
- usage
---

import HeadTitle from '@site/src/components/General/HeadTitle.tsx';

<HeadTitle title="crypto /dd/trades - Reference | OpenBB Terminal Docs" />

Get the latest trades for selected coin

### Usage

```python wordwrap
trades [-e {ace,alpaca,ascendex,bequant,bigone,binance,binancecoinm,binanceus,binanceusdm,bingx,bit2c,bitbank,bitbay,bitbns,bitcoincom,bitfinex,bitfinex2,bitflyer,bitforex,bitget,bithumb,bitmart,bitmex,bitopro,bitpanda,bitrue,bitso,bitstamp,bitstamp1,bittrex,bitvavo,bkex,bl3p,blockchaincom,btcalpha,btcbox,btcmarkets,btctradeua,btcturk,bybit,cex,coinbase,coinbaseprime,coinbasepro,coincheck,coinex,coinfalcon,coinmate,coinone,coinsph,coinspot,cryptocom,currencycom,delta,deribit,digifinex,exmo,fmfwio,gate,gateio,gemini,hitbtc,hitbtc3,hollaex,huobi,huobijp,huobipro,idex,independentreserve,indodax,kraken,krakenfutures,kucoin,kucoinfutures,kuna,latoken,lbank,lbank2,luno,lykke,mercado,mexc,mexc3,ndax,novadax,oceanex,okcoin,okex,okex5,okx,paymium,phemex,poloniex,poloniexfutures,probit,tidex,timex,tokocrypto,upbit,wavesexchange,wazirx,whitebit,woo,yobit,zaif,zonda}] [--vs VS]
```

---

## Parameters

| Name | Parameter | Description | Default | Optional | Choices |
| ---- | --------- | ----------- | ------- | -------- | ------- |
| exchange | -e  --exchange | Exchange to search for order book | binance | True | ace, alpaca, ascendex, bequant, bigone, binance, binancecoinm, binanceus, binanceusdm, bingx, bit2c, bitbank, bitbay, bitbns, bitcoincom, bitfinex, bitfinex2, bitflyer, bitforex, bitget, bithumb, bitmart, bitmex, bitopro, bitpanda, bitrue, bitso, bitstamp, bitstamp1, bittrex, bitvavo, bkex, bl3p, blockchaincom, btcalpha, btcbox, btcmarkets, btctradeua, btcturk, bybit, cex, coinbase, coinbaseprime, coinbasepro, coincheck, coinex, coinfalcon, coinmate, coinone, coinsph, coinspot, cryptocom, currencycom, delta, deribit, digifinex, exmo, fmfwio, gate, gateio, gemini, hitbtc, hitbtc3, hollaex, huobi, huobijp, huobipro, idex, independentreserve, indodax, kraken, krakenfutures, kucoin, kucoinfutures, kuna, latoken, lbank, lbank2, luno, lykke, mercado, mexc, mexc3, ndax, novadax, oceanex, okcoin, okex, okex5, okx, paymium, phemex, poloniex, poloniexfutures, probit, tidex, timex, tokocrypto, upbit, wavesexchange, wazirx, whitebit, woo, yobit, zaif, zonda |
| vs | --vs | Quote currency (what to view coin vs) | usdt | True | AUD, BIDR, BKRW, BNB, BRL, BTC, BUSD, BVND, DAI, DOGE, DOT, ETH, EUR, GBP, IDRT, NGN, PAX, PLN, RUB, TRX, TRY, TUSD, UAH, USDC, USDP, USDS, USDT, UST, VAI, XRP, ZAR |

---
