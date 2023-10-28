---
title: chartsr
description: The '/chartsr' command page provides insights on how the command can
  be utilized by the user to retrieve data on support and resistance levels for the
  given ticker. This can significantly improve their trading decisions.
keywords:
- chartsr command
- support and resistance levels
- ticker trading
- trade decision making
- stock ticker
- trading intervals
- AMC
- 1d interval
---

import HeadTitle from '@site/src/components/General/HeadTitle.tsx';

<HeadTitle title="charts: chartsr - Telegram Reference | OpenBB Bot Docs" />

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
| interval | 5m, 15m, 1d. Default: 1d | True | 5m, 15m, 1d |


---

## Examples

```
/chartsr AMC
```

```
/chartsr AMC 1d
```

---
