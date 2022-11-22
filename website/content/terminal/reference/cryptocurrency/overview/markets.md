---
title: markets
description: OpenBB Terminal Function
---

# markets

Show market related (price, supply, volume) coin information for all coins on CoinPaprika. You can display only N number of coins with --limit parameter. You can sort data by rank, name, symbol, price, volume_24h, mcap_change_24h, pct_change_1h, pct_change_24h, ath_price, pct_from_ath, --sortby parameter and also with --reverse flag to sort ascending. Displays: rank, name, symbol, price, volume_24h, mcap_change_24h, pct_change_1h, pct_change_24h, ath_price, pct_from_ath,

### Usage

```python
usage: markets [--vs {BTC,ETH,USD,EUR,PLN,KRW,GBP,CAD,JPY,RUB,TRY,NZD,AUD,CHF,UAH,HKD,SGD,NGN,PHP,MXN,BRL,THB,CLP,CNY,CZK,DKK,HUF,IDR,ILS,INR,MYR,NOK,PKR,SEK,TWD,ZAR,VND,BOB,COP,PEN,ARS,ISK}] [-l LIMIT]
               [-s {rank,name,symbol,price,volume_24h,mcap_change_24h,pct_change_1h,pct_change_24h,ath_price,pct_from_ath}] [-r]
```

---

## Parameters

| Name | Description | Default | Optional | Choices |
| ---- | ----------- | ------- | -------- | ------- |
| vs | Quoted currency. Default USD | USD | True | BTC, ETH, USD, EUR, PLN, KRW, GBP, CAD, JPY, RUB, TRY, NZD, AUD, CHF, UAH, HKD, SGD, NGN, PHP, MXN, BRL, THB, CLP, CNY, CZK, DKK, HUF, IDR, ILS, INR, MYR, NOK, PKR, SEK, TWD, ZAR, VND, BOB, COP, PEN, ARS, ISK |
| limit | display N number records | 15 | True | None |
| sortby | Sort by given column. Default: rank | rank | True | rank, name, symbol, price, volume_24h, mcap_change_24h, pct_change_1h, pct_change_24h, ath_price, pct_from_ath |
| reverse | Data is sorted in descending order by default. Reverse flag will sort it in an ascending way. Only works when raw data is displayed. | False | True | None |
---

