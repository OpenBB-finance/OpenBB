---
########### THIS FILE IS AUTO GENERATED - ANY CHANGES WILL BE VOID ###########
title: technical
description: OpenBB Discord Command
---

# technical

This command allows the user to retrieve stock screener results according to the chosen technical signal. Specifically, the command "/scr technical signal:Top Gainers" will retrieve the top gainers based on the technical signal chosen. The results of the stock screener can be used to identify stocks that may have potential for price appreciation.

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
