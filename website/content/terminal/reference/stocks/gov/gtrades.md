---
title: gtrades
description: This page provides documentation on how to use the gtrades governmental
  trading tool, offering information on command usage, parameters, and possible settings.
keywords:
- gtrades
- governmental trading
- usage
- parameters
- settings
---

import HeadTitle from '@site/src/components/General/HeadTitle.tsx';

<HeadTitle title="stocks/gov/gtrades - Reference | OpenBB Terminal Docs" />

Government trading. [Source: www.quiverquant.com]

### Usage

```python
gtrades [-p PAST_TRANSACTIONS_MONTHS] [-g {congress,senate,house}] [--raw]
```

---

## Parameters

| Name | Description | Default | Optional | Choices |
| ---- | ----------- | ------- | -------- | ------- |
| past_transactions_months | Past transaction months | 6 | True | None |
| gov |  | congress | True | congress, senate, house |
| raw | Print raw data. | False | True | None |

![gtrades](https://user-images.githubusercontent.com/46355364/154263341-9f51e041-e2c6-408c-bf80-5ef3c7f045f0.png)

---
