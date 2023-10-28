---
title: paexport
description: Detailed usage guide and parameters of the 'paexport' Python command.
  This includes instructions on setting the start and end date, along with the usage
  of different currencies.
keywords:
- paexport
- usage
- parameters
- start date
- end date
- currency
- python
- command
- USD
---

import HeadTitle from '@site/src/components/General/HeadTitle.tsx';

<HeadTitle title="paexport - Degiro - Brokers - Portfolio - Reference | OpenBB Terminal Docs" />

# paexport



### Usage

```python
paexport -s START [-e END] [-c CURRENCY]
```

---

## Parameters

| Name | Description | Default | Optional | Choices |
| ---- | ----------- | ------- | -------- | ------- |
| start | Start date. | None | False | None |
| end | End date. | datetime.now() | True | None |
| currency | Used currency. | USD | True | None |

---
