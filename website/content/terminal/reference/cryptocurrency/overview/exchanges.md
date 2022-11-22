---
title: exchanges
description: OpenBB Terminal Function
---

# exchanges

Shows Top Crypto Exchanges You can display only N number exchanges with --limit parameter. You can sort data by Trust_Score, Id, Name, Country, Year_Established, Trade_Volume_24h_BTC with --sortby Or you can sort data by 'name', 'currencies', 'markets', 'fiats', 'confidence', 'volume_24h', 'volume_7d', 'volume_30d', 'sessions_per_month' if you are using the alternative source CoinPaprika and also with --reverse flag to sort ascending. Flag --urls will display urls. Displays: Trust_Score, Id, Name, Country, Year_Established, Trade_Volume_24h_BTC

### Usage

```python
usage: exchanges [-l LIMIT] [-s {Rank,Trust_Score,Id,Name,Country,Year Established,Trade_Volume_24h_BTC,rank,name,currencies,markets,fiats,confidence,volume_24h,volume_7d,volume_30d,sessions_per_month}] [-r] [-u]
                 [--vs {BTC,ETH,USD,EUR,PLN,KRW,GBP,CAD,JPY,RUB,TRY,NZD,AUD,CHF,UAH,HKD,SGD,NGN,PHP,MXN,BRL,THB,CLP,CNY,CZK,DKK,HUF,IDR,ILS,INR,MYR,NOK,PKR,SEK,TWD,ZAR,VND,BOB,COP,PEN,ARS,ISK}]
```

---

## Parameters

| Name | Description | Default | Optional | Choices |
| ---- | ----------- | ------- | -------- | ------- |
| limit | display N number records | 15 | True | None |
| sortby | Sort by given column. Default: Rank | Rank | True | Rank, Trust_Score, Id, Name, Country, Year Established, Trade_Volume_24h_BTC, rank, name, currencies, markets, fiats, confidence, volume_24h, volume_7d, volume_30d, sessions_per_month |
| reverse | Data is sorted in descending order by default. Reverse flag will sort it in an ascending way. Only works when raw data is displayed. | False | True | None |
| urls | Flag to add a url column. Works only with CoinGecko source | False | True | None |
| vs | Quoted currency. Default: USD. Works only with CoinPaprika source | USD | True | BTC, ETH, USD, EUR, PLN, KRW, GBP, CAD, JPY, RUB, TRY, NZD, AUD, CHF, UAH, HKD, SGD, NGN, PHP, MXN, BRL, THB, CLP, CNY, CZK, DKK, HUF, IDR, ILS, INR, MYR, NOK, PKR, SEK, TWD, ZAR, VND, BOB, COP, PEN, ARS, ISK |
---

