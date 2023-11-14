---
title: create
description: This is a technical page with detailed instructions on how to create
  and use parameters including action, product, symbol, price, size, up_to, duration,
  type, and their respective choices in programming. This covers various market operations
  including buy, sell, GTD, GTC, limit, market, stop-limit, and stop-loss.
keywords:
- create
- usage
- parameters
- action
- product
- symbol
- price
- size
- up_to
- duration
- type
- order
- buy
- sell
- gtd
- gtc
- limit
- market
- stop-limit
- stop-loss
---

import HeadTitle from '@site/src/components/General/HeadTitle.tsx';

<HeadTitle title="portfolio/degiro/create /brokers - Reference | OpenBB Terminal Docs" />



### Usage

```python
create [-a {buy,sell}] (-prod PRODUCT | -sym SYMBOL) -p PRICE (-s SIZE | -up UP_TO) [-d {gtd,gtc}] [-t {limit,market,stop-limit,stop-loss}]
```

---

## Parameters

| Name | Description | Default | Optional | Choices |
| ---- | ----------- | ------- | -------- | ------- |
| action | Action wanted. | buy | True | buy, sell |
| product | Id of the product wanted. | None | True | None |
| symbol | Symbol wanted. | None | True | None |
| price | Price wanted. | None | False | None |
| size | Price wanted. | None | True | None |
| up_to | Up to price. | None | True | None |
| duration | Duration of the Order. | gtd | True | gtd, gtc |
| type | Type of the Order. | limit | True | limit, market, stop-limit, stop-loss |

---
