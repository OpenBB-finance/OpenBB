---
title: cusum
description: The page provides detailed information on using cusum (Cumulative sum
  algorithm) tool. It covers areas such as algorithm usage with Python, parameters
  like threshold and drift, and graphical data representation.
keywords:
- cusum
- cumulative sum algorithm
- data change detection
- algorithm usage
- threshold
- drift
---

import HeadTitle from '@site/src/components/General/HeadTitle.tsx';

<HeadTitle title="forex /qa/cusum - Reference | OpenBB Terminal Docs" />

Cumulative sum algorithm (CUSUM) to detect abrupt changes in data

### Usage

```python wordwrap
cusum [-t THRESHOLD] [-d DRIFT]
```

---

## Parameters

| Name | Parameter | Description | Default | Optional | Choices |
| ---- | --------- | ----------- | ------- | -------- | ------- |
| threshold | -t  --threshold | threshold | 0.002479761838912964 | True | None |
| drift | -d  --drift | drift | 0.001239880919456482 | True | None |

![cusum](https://user-images.githubusercontent.com/46355364/154306207-d68f53f4-2f9a-4c1a-8e0e-b83d49938759.png)

---
