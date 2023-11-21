---
title: eval
description: Create custom data column from loaded datasets
keywords:
- econometrics
- eval
---

import HeadTitle from '@site/src/components/General/HeadTitle.tsx';

<HeadTitle title="econometrics /eval - Reference | OpenBB Terminal Docs" />

Create custom data column from loaded datasets. Can be mathematical expressions supported by pandas.eval() function. Example. If I have loaded `fred DGS2,DGS5` and I want to create a new column that is the difference between these two, I can create a new column by doing `eval spread = DGS2 - DGS5`. Notice that the command is case sensitive, i.e., `DGS2` is not the same as `dgs2`.

### Usage

```python wordwrap
eval -q QUERY [QUERY ...]
```

---

## Parameters

| Name | Parameter | Description | Default | Optional | Choices |
| ---- | --------- | ----------- | ------- | -------- | ------- |
| query | -q  --query | Query to evaluate on loaded datasets | None | False | None |

---
