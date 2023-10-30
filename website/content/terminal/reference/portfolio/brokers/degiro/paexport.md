---
title: paexport
description: Detailed usage guide and parameters of the 'paexport' Python command.
  This includes instructions on setting the start and end date, along with the usage
  of different currencies.
keywords:
- paexport
- usage
- parameters
- currency
- USD
---

import HeadTitle from '@site/src/components/General/HeadTitle.tsx';

<HeadTitle title="portfolio/degiro/paexport /brokers - Reference | OpenBB Terminal Docs" />



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
