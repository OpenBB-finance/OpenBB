---
title: screener
description: The screener command page offers guidance to users on how to retrieve
  stock screener results using different technical signals. It includes various screener
  signals like Top Gainers, Top Losers, Most Active, etc.
keywords:
- Screener Command
- Stock Screener Results
- Technical Signals
- Top Gainers
- Top Losers
- Most Active
---

import HeadTitle from '@site/src/components/General/HeadTitle.tsx';

<HeadTitle title="screeners: screener - Telegram Reference | OpenBB Bot Docs" />

This command allows the user to retrieve stock screener results according to the chosen technical signal.

### Usage

```python wordwrap
/screener signal
```

---

## Parameters

| Name | Description | Optional | Choices |
| ---- | ----------- | -------- | ------- |
| signal | Screener Signal | False | 1 : Top Gainers, 2 : Top Losers, 3 : Most Active, 4 : Most Volatile, 5 : Relative Volatility, 6 : Golden Cross, 7 : Death Cross, 8 : New 52week High, 9 : New 52week Low, 10 : Unusual Volume |

---

## Examples

```
/screener 0
```
```
/screener 4
```
---
