---
title: index
description: Set a (multi) index for the dataset
keywords:
- econometrics
- index
---

import HeadTitle from '@site/src/components/General/HeadTitle.tsx';

<HeadTitle title="econometrics /index - Reference | OpenBB Terminal Docs" />

Set a (multi) index for the dataset

### Usage

```python wordwrap
index -n {} [-i INDEX] [-a] [-d]
```

---

## Parameters

| Name | Parameter | Description | Default | Optional | Choices |
| ---- | --------- | ----------- | ------- | -------- | ------- |
| name | -n  --name | Name of dataset to select index from | None | False | None |
| index | -i  --index | Columns from the dataset the user wishes to set as default |  | True | None |
| adjustment | -a  --adjustment | Whether to allow for making adjustments to the dataset to align it with the use case for Timeseries and Panel Data regressions | False | True | None |
| drop | -d  --drop | Whether to drop the column(s) the index is set for. | False | True | None |

---
