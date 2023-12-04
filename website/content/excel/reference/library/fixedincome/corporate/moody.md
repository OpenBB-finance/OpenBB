---
title: moody
description: Moody Corporate Bond Index
keywords: 
- fixedincome
- corporate
- moody
---

<!-- markdownlint-disable MD041 -->

Moody Corporate Bond Index.  Moody's Aaa and Baa are investment bonds that acts as an index of the performance of all bonds given an Aaa or Baa rating by Moody's Investors Service respectively. These corporate bonds often are used in macroeconomics as an alternative to the federal ten-year Treasury Bill as an indicator of the interest rate.

## Syntax

```excel wordwrap
=OBB.FIXEDINCOME.CORPORATE.MOODY(required;[optional])
```

---

## Parameters

| Name | Type | Description | Optional |
| ---- | ---- | ----------- | -------- |
| provider | Text | Options: fred | True |
| start_date | Text | Start date of the data, in YYYY-MM-DD format. | True |
| end_date | Text | End date of the data, in YYYY-MM-DD format. | True |
| index_type | Text | The type of series. | True |
| spread | Text | The type of spread. (provider: fred) | True |

---

## Return Data

| Name | Description |
| ---- | ----------- |
| date | The date of the data.  |
| rate | Moody Corporate Bond Index Rate.  |
