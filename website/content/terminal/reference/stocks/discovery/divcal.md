---
title: divcal
description: OpenBB Terminal Function
---

# divcal

Get dividend calendar for selected date

### Usage

```python
usage: divcal [-d DATE] [-s {name,symbol,ex-dividend_date,payment_date,record_date,dividend,annual_dividend,announcement_date}] [-r]
```

---

## Parameters

| Name | Description | Default | Optional | Choices |
| ---- | ----------- | ------- | -------- | ------- |
| date | Date to get format for | datetime.now() | True | None |
| sort | Column to sort by | dividend | True | name, symbol, ex-dividend_date, payment_date, record_date, dividend, annual_dividend, announcement_date |
| reverse | Data is sorted in descending order by default. Reverse flag will sort it in an ascending way. Only works when raw data is displayed. | False | True | None |
---

