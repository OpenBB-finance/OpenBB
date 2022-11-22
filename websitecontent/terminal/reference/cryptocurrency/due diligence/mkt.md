---
title: mkt
description: OpenBB Terminal Function
---

# mkt

Get all markets found for given coin. You can display only N number of markets with --limt parameter. You can sort data by pct_volume_share, exchange, pair, trust_score, volume, price --sort parameter and also with --reverse flag to sort ascending. You can use additional flag --urls to see urls for each market Displays: exchange, pair, trust_score, volume, price, pct_volume_share,

### Usage

```python
usage: mkt [--vs {BTC,ETH,USD,EUR,PLN,KRW,GBP,CAD,JPY,RUB,TRY,NZD,AUD,CHF,UAH,HKD,SGD,NGN,PHP,MXN,BRL,THB,CLP,CNY,CZK,DKK,HUF,IDR,ILS,INR,MYR,NOK,PKR,SEK,TWD,ZAR,VND,BOB,COP,PEN,ARS,ISK}] [-l LIMIT]
           [-s {pct_volume_share,exchange,pair,trust_score,volume,price}] [-r] [-u]
```

---

## Parameters

| Name | Description | Default | Optional | Choices |
| ---- | ----------- | ------- | -------- | ------- |
| vs | Quoted currency. Default USD | USD | True | BTC, ETH, USD, EUR, PLN, KRW, GBP, CAD, JPY, RUB, TRY, NZD, AUD, CHF, UAH, HKD, SGD, NGN, PHP, MXN, BRL, THB, CLP, CNY, CZK, DKK, HUF, IDR, ILS, INR, MYR, NOK, PKR, SEK, TWD, ZAR, VND, BOB, COP, PEN, ARS, ISK |
| limit | Limit of records | 20 | True | None |
| sortby | Sort by given column. Default: pct_volume_share | pct_volume_share | True | pct_volume_share, exchange, pair, trust_score, volume, price |
| reverse | Data is sorted in descending order by default. Reverse flag will sort it in an ascending way. Only works when raw data is displayed. | False | True | None |
| urls | Flag to show urls. If you will use that flag you will see only: exchange, pair, trust_score, market_url columns | False | True | None |
---

