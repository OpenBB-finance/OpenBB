---
title: technical
description: Learn how to use the command for retrieving stock screener results based
  on your choice of a technical signal. Provides information on how to use technical
  signals like Top Gainers, Top Losers, Most Active, among others.
keywords:
- stock screener
- technical signal
- Top Gainers
- Top Losers
- Most Active
- Most Volatile
- Relative Volatility
- Oversold (RSI 30)
- Overbought (RSI 70)
- Golden Cross
- Death Cross
- New 52week High
- New 52week Low
- Unusual Volume
---

import HeadTitle from '@site/src/components/General/HeadTitle.tsx';

<HeadTitle title="screeners: technical - Discord Reference | OpenBB Bot Docs" />

This command allows the user to retrieve stock screener results according to the chosen technical signal.

### Usage

```python wordwrap
/scr technical signal
```

---

## Parameters

| Name | Description | Optional | Choices |
| ---- | ----------- | -------- | ------- |
| signal | screener preset | False | Top Gainers (gainers), Top Losers (losers), Most Active (most_active), Most Volatile (most_volatile), Relative Volatility (relative_volatility), Oversold (RSI  30) (oversold), Overbought (RSI  70) (overbought), Golden Cross (golden_cross), Death Cross (death_cross), New 52week High (new_w52high), New 52week Low (new_w52low), Unusual Volume (unusual_volume) |


---

## Examples

```
/scr technical signal:Top Gainers
```
```
/scr technical signal:Death Cross
```

---
