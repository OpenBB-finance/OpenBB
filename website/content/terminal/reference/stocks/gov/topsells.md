---
title: topsells
description: The page provides information on the top sells in government trading.
  Understand how to use different options like governing body, limit of top tickers,
  past transaction months and others to filter the information.
keywords:
- government trading
- top sells
- congress
- senate
- house
- past transactions months
- limit of top tickers
- print raw data
- quiverquant
---

import HeadTitle from '@site/src/components/General/HeadTitle.tsx';

<HeadTitle title="stocks/gov/topsells - Reference | OpenBB Terminal Docs" />

Top sells for government trading. [Source: www.quiverquant.com]

### Usage

```python
topsells [-g {congress,senate,house}] [-p PAST_TRANSACTIONS_MONTHS] [-l LIMIT] [--raw]
```

---

## Parameters

| Name | Description | Default | Optional | Choices |
| ---- | ----------- | ------- | -------- | ------- |
| gov |  | congress | True | congress, senate, house |
| past_transactions_months | Past transaction months | 6 | True | None |
| limit | Limit of top tickers to display | 10 | True | None |
| raw | Print raw data. | False | True | None |

![topsells](https://user-images.githubusercontent.com/46355364/154266942-4ee9c83a-39be-4aab-8a06-01b6850f5bd9.png)

---
