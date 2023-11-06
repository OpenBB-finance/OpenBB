---
title: summary
description: Learn how to retrieve a summary of all the prints by percentage of MarketCap
  over the last x days, sorted by MarketCap. Understand the usage, parameters, and
  see examples.
keywords:
- prints summary
- MarketCap
- Sort by MarketCap
- /dp summary command
- MarketCap over time
- Market analysis
- Financial Data Analysis
- Short Percentage
- Float
---

import HeadTitle from '@site/src/components/General/HeadTitle.tsx';

<HeadTitle title="darkpool: summary - Discord Reference | OpenBB Bot Docs" />

This command retrieves a summary of all the prints by percentage of MarketCap over the last x days, sorted by MarketCap. The summary includes the total number of prints and their total percentage of MarketCap, as well as the float and short percentage.

### Usage

```python wordwrap
/dp summary days sort
```

---

## Parameters

| Name | Description | Optional | Choices |
| ---- | ----------- | -------- | ------- |
| days | Number of days to look back | False | None |
| sort | Sort by MarketCap, Float, Total, or Short Percentage | False | MarketCap (mc), Float (float), Total (sum), Short Percentage (short) |


---

## Examples

```
/dp summary days:10 sort:MarketCap
```

---
