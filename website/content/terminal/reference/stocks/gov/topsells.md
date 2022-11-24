---
title: topsells
description: OpenBB Terminal Function
---

# topsells

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
