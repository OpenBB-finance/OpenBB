---
title: chartsr
description: The chartsr command allows the user to retrieve Displays Support and
  Resistance Levels for any given ticker. Useful in making informed trading decisions.
keywords:
- chartsr
- Support and Resistance Levels
- trading
- trading decisions
- Stock Ticker
- Chart Interval
---

import HeadTitle from '@site/src/components/General/HeadTitle.tsx';

<HeadTitle title="charts: chartsr - Discord Reference | OpenBB Bot Docs" />

This command allows the user to retrieve Displays Support and Resistance Levels for the ticker provided. It will display the support and resistance levels of a given ticker on the chart. These levels can help the user in making better trading decisions.

### Usage

```python wordwrap
/chartsr ticker [interval]
```

---

## Parameters

| Name | Description | Optional | Choices |
| ---- | ----------- | -------- | ------- |
| ticker | Stock Ticker | False | None |
| interval | Chart Interval | True | 5 minute (5), 15 minute (15) |


---

## Examples

```
/chartsr ticker:AMC
```
```
/chartsr ticker:AMC interval:5 minute
```

---
