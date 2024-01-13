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

```jsx<span style={color: 'red'}>=OBB.FIXEDINCOME.CORPORATE.MOODY([provider];[start_date];[end_date];[index_type];[spread])</span>```

### Example

```excel wordwrap
=OBB.FIXEDINCOME.CORPORATE.MOODY()
```

---

## Parameters

| Name | Type | Description | Optional |
| ---- | ---- | ----------- | -------- |
| provider | Text | Options: fred, defaults to fred. | True |
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
