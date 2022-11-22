---
title: treasury
description: OpenBB Terminal Function
---

# treasury

Obtain any set of U.S. treasuries and plot them together. These can be a range of maturities for nominal, inflation-adjusted (on long term average of inflation adjusted) and secondary markets over a lengthy period. Note: 3-month and 10-year treasury yields for other countries are available via the command 'macro' and parameter 'M3YD' and 'Y10YD'. [Source: EconDB / FED]

### Usage

```python
usage: treasury [-m MATURITY] [--show] [--freq {annually,monthly,weekly,daily}] [-t TYPE] [-s START_DATE] [-e END_DATE]
```

---

## Parameters

| Name | Description | Default | Optional | Choices |
| ---- | ----------- | ------- | -------- | ------- |
| maturity | The preferred maturity which is dependent on the type of the treasury | 10y | True | None |
| show_maturities | Show the maturities available for every instrument. | False | True | None |
| frequency | The frequency, this can be annually, monthly, weekly or daily | monthly | True | annually, monthly, weekly, daily |
| type | Choose from: nominal, inflation, average, secondary | nominal | True | None |
| start_date | The start date of the data (format: YEAR-MONTH-DAY, i.e. 2010-12-31) | 1934-01-31 | True | None |
| end_date | The end date of the data (format: YEAR-DAY-MONTH, i.e. 2021-06-02) | 2022-11-22 | True | None |
---

