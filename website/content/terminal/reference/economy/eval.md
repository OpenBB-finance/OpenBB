---
title: eval
description: This page provides information about the 'eval' function for creating
  custom data columns using mathematical expressions supported by pandas.eval(). It
  exemplifies case sensitivity and the use of queries on loaded datasets.
keywords:
- eval function
- custom data column
- pandas.eval
- mathematical expressions
- datasets
- case sensitive
- query
- DGS2
- DGS5
---

import HeadTitle from '@site/src/components/General/HeadTitle.tsx';

<HeadTitle title="economy /eval - Reference | OpenBB Terminal Docs" />

Create custom data column from loaded datasets. Can be mathematical expressions supported by pandas.eval() function. Example. If I have loaded `fred DGS2,DGS5` and I want to create a new column that is the difference between these two, I can create a new column by doing `eval spread = DGS2 - DGS5`. Notice that the command is case sensitive, i.e., `DGS2` is not the same as `dgs2`.

### Usage

```python
eval [-q QUERY [QUERY ...]]
```

---

## Parameters

| Name | Description | Default | Optional | Choices |
| ---- | ----------- | ------- | -------- | ------- |
| query | Query to evaluate on loaded datasets | None | False | None |

---
