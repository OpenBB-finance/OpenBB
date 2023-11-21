---
title: cusum
description: This page provides a detailed explanation on the usage, parameters and
  functionality of the Cumulative Sum Algorithm (CUSUM) used for detecting abrupt
  changes in data.
keywords:
- cusum
- cumulative sum algorithm
- data change detection
- threshold
- drift
---

import HeadTitle from '@site/src/components/General/HeadTitle.tsx';

<HeadTitle title="economy /qa/cusum - Reference | OpenBB Terminal Docs" />

Cumulative sum algorithm (CUSUM) to detect abrupt changes in data

### Usage

```python wordwrap
cusum [-t THRESHOLD] [-d DRIFT]
```

---

## Parameters

| Name | Parameter | Description | Default | Optional | Choices |
| ---- | --------- | ----------- | ------- | -------- | ------- |
| threshold | -t  --threshold | threshold | 1.7601984105623987 | True | None |
| drift | -d  --drift | drift | 0.8800992052811993 | True | None |

![cusum](https://user-images.githubusercontent.com/46355364/154306207-d68f53f4-2f9a-4c1a-8e0e-b83d49938759.png)

---
