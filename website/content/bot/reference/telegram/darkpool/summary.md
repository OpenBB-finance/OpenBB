---
title: summary
description: Documentation page for the '/summary' command, which retrieves a summary
  of all prints by MarketCap percentage. The command and its parameters 'days' and
  'sort' are explained. The description provides various options for sorting, i.e.,
  by MarketCap, float, sum, or short percentage.
keywords:
- MarketCap Summary
- Prints by MarketCap
- Prints Summary
- Command /summary
- Parameter days
- Parameter sort
- Sort by MarketCap
- Sort by float
- Sort by sum
- Sort by short percentage
---

import HeadTitle from '@site/src/components/General/HeadTitle.tsx';

<HeadTitle title="darkpool: summary - Telegram Reference | OpenBB Bot Docs" />

This command retrieves a summary of all the prints by percentage of MarketCap over the last x days, sorted by MarketCap. The summary includes the total number of prints and their total percentage of MarketCap, as well as the float and short percentage.

### Usage

```python wordwrap
/summary days sort
```

---

## Parameters

| Name | Description | Optional | Choices |
| ---- | ----------- | -------- | ------- |
| days | Number of days to look back | False | None |
| sort | Sort by `mc` (MarketCap), `float`, `sum`, or `short` (Short Percentage) | False | None |


---

## Examples

```
/summary 10 mc
```

---
