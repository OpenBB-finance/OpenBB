---
title: index
description: OpenBB Terminal Function
---

# index

Set a (multi) index for the dataset

### Usage

```python
usage: index -n {} [-i INDEX] [-a] [-d]
```

---

## Parameters

| Name | Description | Default | Optional | Choices |
| ---- | ----------- | ------- | -------- | ------- |
| name | Name of dataset to select index from | None | False | None |
| index | Columns from the dataset the user wishes to set as default |  | True | None |
| adjustment | Whether to allow for making adjustments to the dataset to align it with the use case for Timeseries and Panel Data regressions | False | True | None |
| drop | Whether to drop the column(s) the index is set for. | False | True | None |
---

