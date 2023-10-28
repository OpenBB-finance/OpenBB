---
title: levels
description: This page provides information about the 'levels' command that allows
  users to retrieve the Biggest Levels for All Prints over the last x days for a given
  stock ticker. This command aids in evaluating stock performance.
keywords:
- levels command
- DP levels
- stock ticker
- stock performance
- All Prints
- Biggest Levels
- usage of levels command
- parameters
- examples
---

import HeadTitle from '@site/src/components/General/HeadTitle.tsx';

<HeadTitle title="darkpool: levels - Discord Reference | OpenBB Bot Docs" />

This command allows the user to retrieve the Biggest Levels for All Prints over the last x days for the given ticker. This information is useful in assessing the overall performance of the stock, as it provides information on the largest levels of prints over the last x days.

### Usage

```python wordwrap
/dp levels ticker days
```

---

## Parameters

| Name | Description | Optional | Choices |
| ---- | ----------- | -------- | ------- |
| ticker | Stock Ticker | False | None |
| days | Number of days to look back | False | None |


---

## Examples

```
/dp levels ticker:TSLA days:10
```

---
