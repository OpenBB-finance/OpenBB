---
title: index
description: OpenBB Terminal Function
---

# index

Obtain any set of indices and plot them together. With the -si argument the major indices are shown. By using the arguments (for example 'nasdaq' and 'sp500') you can collect data and plot the graphs together. [Source: Yahoo finance / FinanceDatabase]

### Usage

```python
usage: index [-i INDICES] [--show] [--interval {1m,2m,5m,15m,30m,60m,90m,1h,1d,5d,1wk,1mo,3mo}] [-s START_DATE] [-e END_DATE] [-c COLUMN] [-q QUERY] [-r]
```

---

## Parameters

| Name | Description | Default | Optional | Choices |
| ---- | ----------- | ------- | -------- | ------- |
| indices | One or multiple indices | None | True | None |
| show_indices | Show the major indices, their arguments and ticker | False | True | None |
| interval | The preferred interval data is shown at. This can be 1m, 2m, 5m, 15m, 30m, 60m, 90m, 1h, 1d, 5d, 1wk, 1mo or 3mo | 1d | True | 1m, 2m, 5m, 15m, 30m, 60m, 90m, 1h, 1d, 5d, 1wk, 1mo, 3mo |
| start_date | The start date of the data (format: YEAR-MONTH-DAY, i.e. 2010-12-31) | 2000-01-01 | True | None |
| end_date | The end date of the data (format: YEAR-MONTH-DAY, i.e. 2021-06-20) | None | True | None |
| column | The column you wish to load in, by default this is the Adjusted Close column | Adj Close | True | None |
| query | Search for indices with given keyword | None | True | None |
| returns | Flag to show compounded returns over interval. | False | True | None |
---

