---
title: treasury
description: Plot short (3 month) and long (10 year) term interest rates from selected countries including the possibility to plot forecasts for the next years
keywords:
- fixedincome
- treasury
---

import HeadTitle from '@site/src/components/General/HeadTitle.tsx';

<HeadTitle title="fixedincome /treasury - Reference | OpenBB Terminal Docs" />

Plot short (3 month) and long (10 year) term interest rates from selected countries including the possibility to plot forecasts for the next years.

### Usage

```python wordwrap
treasury [--short SHORT] [--long LONG] [-s START_DATE] [-e END_DATE] [--forecast]
```

---

## Parameters

| Name | Parameter | Description | Default | Optional | Choices |
| ---- | --------- | ----------- | ------- | -------- | ------- |
| short | --short | Countries to get short term (3 month) interest rates for. | None | True | None |
| long | --long | Countries to get long term (10 year) interest rates for. | None | True | None |
| start_date | -s  --start | Start date of data, in YYYY-MM-DD format | None | True | None |
| end_date | -e  --end | End date of data, in YYYY-MM-DD format | None | True | None |
| forecast | --forecast | If True, plot forecasts for each interest rate | False | True | None |

---
