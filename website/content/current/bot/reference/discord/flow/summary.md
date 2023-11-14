---
title: summary
description: The page offers instructions on using a command that retrieves a summary
  of all the flow per stock in the last x days. The summary includes details like
  the ratio to total market capitalization, number of trades, etc. and the result
  can be sorted in various ways like MarketCap, Float, and more.
keywords:
- Flow per stock
- Total market capitalization
- Number of trades
- Sort by MarketCap
- Sort by Float
- Sort by Total
- Sort by Short Percentage
- Command usage
---

import HeadTitle from '@site/src/components/General/HeadTitle.tsx';

<HeadTitle title="flow: summary - Discord Reference | OpenBB Bot Docs" />

This command allows the user to retrieve a summary of all the flow per stock over the last x days, with the result sorted in various ways. This summary will include the ratio to total market capitalization, the number of trades, and other information.

### Usage

```python wordwrap
/flow summary days sort
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
/flow summary days:5 sort:Float
```

```
/flow summary days:5 sort:Short Percentage
```

---
