---
title: eval
description: OpenBB Terminal Function
---

# eval

Create custom data column from loaded datasets. Can be mathematical expressions supported by pandas.eval() function. Example. If I have loaded `fred DGS2,DGS5` and I want to create a new column that is the difference between these two, I can create a new column by doing `eval spread = DGS2 - DGS5`. Notice that the command is case sensitive, i.e., `DGS2` is not the same as `dgs2`.

### Usage

```python
eval [-q QUERY [QUERY ...]]
```

---

## Parameters

| Name | Description | Default | Optional | Choices |
| ---- | ----------- | ------- | -------- | ------- |
| query | Query to evaluate on loaded datasets | None | True | None |

---
