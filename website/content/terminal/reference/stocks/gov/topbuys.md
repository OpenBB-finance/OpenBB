---
title: topbuys
description: Explore top buys for government trading. Discover how to use the 'topbuys'
  feature, including parameter selection for congress, senate and house, past transactions,
  and more for optimized use. Enhance your trading strategies today with quiverquant.
keywords:
- government trading
- topbuys
- congress
- senate
- house
- past transactions
- quiverquant
---

import HeadTitle from '@site/src/components/General/HeadTitle.tsx';

<HeadTitle title="stocks/gov/topbuys - Reference | OpenBB Terminal Docs" />

Top buys for government trading. [Source: www.quiverquant.com]

### Usage

```python
topbuys [-g {congress,senate,house}] [-p PAST_TRANSACTIONS_MONTHS] [-l LIMIT] [--raw]
```

---

## Parameters

| Name | Description | Default | Optional | Choices |
| ---- | ----------- | ------- | -------- | ------- |
| gov |  | congress | True | congress, senate, house |
| past_transactions_months | Past transaction months | 6 | True | None |
| limit | Limit of top tickers to display | 10 | True | None |
| raw | Print raw data. | False | True | None |

![topbuys](https://user-images.githubusercontent.com/46355364/154266344-944b0c5b-f7b0-4fdb-a020-a93565f6c13c.png)

---
