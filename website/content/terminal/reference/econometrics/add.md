---
title: add
description: OpenBB Terminal Function
---

# add

Add columns to your dataframe with the option to use formulas. E.g. newdatasetcol = basedatasetcol sign criteriaordatasetcol thesis.high_revenue = thesis.revenue  1000 dataset.debt_ratio = dataset.debt div dataset2.assets

### Usage

```python
usage: add -n NEWDATASETCOL -b BASEDATASETCOL -s {div,mul,add,sub,mod,pow,,,=,=,==} -c CRITERIAORDATASETCOL
```

---

## Parameters

| Name | Description | Default | Optional | Choices |
| ---- | ----------- | ------- | -------- | ------- |
| newdatasetcol | New dataset column to be added with format: dataset.column | None | False | None |
| basedatasetcol | Base dataset column to be used as base with format: dataset.column | None | False | None |
| sign | Sign to be applied to the base dataset column | None | False | div, mul, add, sub, mod, pow, , , =, =, == |
| criteriaordatasetcol | Either dataset column to be applied on top of base dataset or criteria | None | False | None |
---

