---
title: root
description: OpenBB Terminal Function
---

# root

Show unit root tests of a column of a dataset

### Usage

```python
usage: root -v {} [-r {c,ct,ctt,n}] [-k {c,ct}]
```

---

## Parameters

| Name | Description | Default | Optional | Choices |
| ---- | ----------- | ------- | -------- | ------- |
| column | The column and name of the database you want test unit root for | None | False | None |
| fuller_reg | Type of regression. Can be 'c','ct','ctt','nc'. c - Constant and t - trend order | c | True | c, ct, ctt, n |
| kpss_reg | Type of regression. Can be 'c', 'ct'. c - Constant and t - trend order | c | True | c, ct |
---

