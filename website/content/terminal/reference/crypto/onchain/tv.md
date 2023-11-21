---
title: tv
description: This section of the page is a guide on using the function to display
  token volume on different Decentralized Exchanges. It includes parameters such as
  the currency of the displayed trade amount and options to sort data.
keywords:
- decentralized exchanges
- token volume
- ERC20 token
- trade amount
- sort by column
- data sorting
---

import HeadTitle from '@site/src/components/General/HeadTitle.tsx';

<HeadTitle title="crypto /onchain/tv - Reference | OpenBB Terminal Docs" />

Display token volume on different Decentralized Exchanges. [Source: https://graphql.bitquery.io/]

### Usage

```python wordwrap
tv -c COIN [-vs {ETH,USD,BTC,USDT}] [-l LIMIT] [-s {exchange,trades,tradeAmount}] [-r]
```

---

## Parameters

| Name | Parameter | Description | Default | Optional | Choices |
| ---- | --------- | ----------- | ------- | -------- | ------- |
| coin | -c  --coin | ERC20 token symbol or address. | None | False | None |
| vs | -vs  --vs | Currency of displayed trade amount. | USD | True | ETH, USD, BTC, USDT |
| limit | -l  --limit | display N number records | 10 | True | None |
| sortby | -s  --sort | Sort by given column. | trades | True | exchange, trades, tradeAmount |
| reverse | -r  --reverse | Data is sorted in descending order by default. Reverse flag will sort it in an ascending way. Only works when raw data is displayed. | False | True | None |

---
