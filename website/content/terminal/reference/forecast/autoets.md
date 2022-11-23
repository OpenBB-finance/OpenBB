---
title: autoets
description: OpenBB Terminal Function
---

# autoets

Perform Automatic ETS (Error, Trend, Seasonality) forecast: https://nixtla.github.io/statsforecast/examples/getting_started_with_auto_arima_and_ets.html

### Usage

```python
usage: autoets
```

---

## Parameters

This command has no parameters



---

## Examples

```python
2022 Oct 21, 18:20 (🦋) /forecast/ $ load AAPL

2022 Oct 21, 18:21 (🦋) /forecast/ $ autoets AAPL



   Actual price: 143.39
┏━━━━━━━━━━━━┳━━━━━━━━━━━━┓
┃ Datetime   ┃ Prediction ┃
┡━━━━━━━━━━━━╇━━━━━━━━━━━━┩
│ 2022-10-21 │ 143.42     │
├────────────┼────────────┤
│ 2022-10-24 │ 143.42     │
├────────────┼────────────┤
│ 2022-10-25 │ 143.42     │
├────────────┼────────────┤
│ 2022-10-26 │ 143.42     │
├────────────┼────────────┤
│ 2022-10-27 │ 143.42     │
└────────────┴────────────┘
```
![autoets](https://user-images.githubusercontent.com/10517170/197297075-d141d735-0b35-43cc-bf4f-e746b6b1001e.png)

---
