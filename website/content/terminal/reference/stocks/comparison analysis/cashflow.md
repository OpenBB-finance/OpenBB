---
title: cashflow
description: OpenBB Terminal Function
---

# cashflow

Prints either yearly or quarterly cashflow statement the company, and compares it against similar companies.

### Usage

```python
usage: cashflow [-q] [-t S_TIMEFRAME]
```

---

## Parameters

| Name | Description | Default | Optional | Choices |
| ---- | ----------- | ------- | -------- | ------- |
| b_quarter | Quarter financial data flag. | False | True | None |
| s_timeframe | Specify year/quarter of the cashflow statement to be retrieved. The format for year is YYYY and for quarter is DD-MMM-YYY (for example, 30-Sep-2021). Default is last year/quarter. | None | True | None |
---

