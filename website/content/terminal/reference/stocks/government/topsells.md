---
title: topsells
description: OpenBB Terminal Function
---

# topsells

Top sells for government trading. [Source: www.quiverquant.com]

### Usage

```python
usage: topsells [-g {congress,senate,house}] [-p PAST_TRANSACTIONS_MONTHS] [-l LIMIT] [--raw]
```

---

## Parameters

| Name | Description | Default | Optional | Choices |
| ---- | ----------- | ------- | -------- | ------- |
| gov |  | congress | True | congress, senate, house |
| past_transactions_months | Past transaction months | 6 | True | None |
| limit | Limit of top tickers to display | 10 | True | None |
| raw | Print raw data. | False | True | None |
---

