---
title: lt
description: Description and usage guide for the lt command, that displays trades
  on decentralized exchanges including the ability to aggregate trades by DEX or time,
  display trade amount in different currencies, and sort data. The command uses Python
  language.
keywords:
- Display Trades
- Decentralized Exchanges
- Aggregated
- DEX
- Trade Amount
- Currency
- USD
- ETH
- BTC
- USDT
---

import HeadTitle from '@site/src/components/General/HeadTitle.tsx';

<HeadTitle title="crypto/onchain/lt - Reference | OpenBB Terminal Docs" />

Display Trades on Decentralized Exchanges aggregated by DEX or Month [Source: https://graphql.bitquery.io/]

### Usage

```python
lt [-k {dex,time}] [-vs {ETH,USD,BTC,USDT}] [-l LIMIT] [-d DAYS] [-s {exchange,trades,tradeAmount}] [-r]
```

---

## Parameters

| Name | Description | Default | Optional | Choices |
| ---- | ----------- | ------- | -------- | ------- |
| kind | Aggregate trades by dex or time Default: dex | dex | True | dex, time |
| vs | Currency of displayed trade amount. | USD | True | ETH, USD, BTC, USDT |
| limit | display N number records | 10 | True | None |
| days | Number of days to display data for. | 90 | True | range(1, 360) |
| sortby | Sort by given column. Default: tradeAmount. For monthly trades date. | tradeAmount | True | exchange, trades, tradeAmount |
| reverse | Data is sorted in descending order by default. Reverse flag will sort it in an ascending way. Only works when raw data is displayed. | False | True | None |

---
