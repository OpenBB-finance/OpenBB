---
title: so
description: This page provides information on how to calculate the Sortino ratio
  of a selected stock, including parameters for target return, adjusting the Sortino
  ratio for comparison with the Sharpe ratio, and setting the rolling window length.
keywords:
- sortino ratio
- stock analysis
- target return
- adjusted sortino ratio
- rolling window length
- sharpe ratio
- investment strategy
---

import HeadTitle from '@site/src/components/General/HeadTitle.tsx';

<HeadTitle title="stocks/qa/so - Reference | OpenBB Terminal Docs" />

Provides the sortino ratio of the selected stock.

### Usage

```python
so [-t TARGET_RETURN] [-a] [-w WINDOW]
```

---

## Parameters

| Name | Description | Default | Optional | Choices |
| ---- | ----------- | ------- | -------- | ------- |
| target_return | Target return | 0 | True | None |
| adjusted | If one should adjust the sortino ratio inorder to make it comparable to the sharpe ratio | False | True | None |
| window | Rolling window length | 1 | True | None |

![image](https://user-images.githubusercontent.com/75195383/163530572-e527bc75-7ecd-44e3-b971-83b9a0662d0d.png)

---
