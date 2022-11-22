---
title: clean
description: OpenBB Terminal Function
---

# clean

Clean a dataset by filling and dropping NaN values.

### Usage

```python
usage: clean [-n {}] [--fill {rfill,cfill,rbfill,cbfill,rffill,bffill}] [-d {rdrop,cdrop}]
```

---

## Parameters

| Name | Description | Default | Optional | Choices |
| ---- | ----------- | ------- | -------- | ------- |
| name | The name of the dataset you want to clean up | None | True | None |
| fill | The method of filling NaNs. This has options to fill rows (rfill, rbfill, rffill) or fill columns (cfill, cbfill, cffill). Furthermore, it has the option to forward fill and backward fill (up to --limit) which refer to how many rows/columns can be set equal to the last non-NaN value |  | True | rfill, cfill, rbfill, cbfill, rffill, bffill |
| drop | The method of dropping NaNs. This either has the option rdrop (drop rows that contain NaNs) or cdrop (drop columns that contain NaNs) |  | True | rdrop, cdrop |
---

