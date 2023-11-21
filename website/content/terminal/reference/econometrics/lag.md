---
title: lag
description: Add lag to a variable by shifting a column
keywords:
- econometrics
- lag
---

import HeadTitle from '@site/src/components/General/HeadTitle.tsx';

<HeadTitle title="econometrics /lag - Reference | OpenBB Terminal Docs" />

Add lag to a variable by shifting a column.

### Usage

```python wordwrap
lag -v {} -l LAGS [-f FILL_VALUE]
```

---

## Parameters

| Name | Parameter | Description | Default | Optional | Choices |
| ---- | --------- | ----------- | ------- | -------- | ------- |
| values | -v  --values | Dataset.column values to add lag to. | None | False | None |
| lags | -l  --lags | How many periods to lag the selected column. | 5 | False | None |
| fill_value | -f  --fill-value | The value used for filling the newly introduced missing values. | None | True | None |

---
