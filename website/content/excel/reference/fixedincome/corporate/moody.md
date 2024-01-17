---
title: MOODY
description: Moody Corporate Bond Index
keywords: 
- fixedincome
- corporate
- moody
---

<!-- markdownlint-disable MD033 -->
import HeadTitle from '@site/src/components/General/HeadTitle.tsx';

<HeadTitle title="FIXEDINCOME.CORPORATE.MOODY | OpenBB Add-in for Excel Docs" />

Moody Corporate Bond Index.  Moody's Aaa and Baa are investment bonds that acts as an index of the performance of all bonds given an Aaa or Baa rating by Moody's Investors Service respectively. These corporate bonds often are used in macroeconomics as an alternative to the federal ten-year Treasury Bill as an indicator of the interest rate.

## Syntax

```excel wordwrap
=OBB.FIXEDINCOME.CORPORATE.MOODY([start_date];[end_date];[index_type];[provider];[spread])
```

### Example

```excel wordwrap
=OBB.FIXEDINCOME.CORPORATE.MOODY()
```

---

## Parameters

| Name | Type | Description | Required |
| ---- | ---- | ----------- | -------- |
| start_date | Text | Start date of the data, in YYYY-MM-DD format. | False |
| end_date | Text | End date of the data, in YYYY-MM-DD format. | False |
| index_type | Text | The type of series. | False |
| provider | Text | Options: fred, defaults to fred. | False |
| spread | Text | The type of spread. (provider: fred) | False |

---

## Return Data

| Name | Description |
| ---- | ----------- |
| date | The date of the data.  |
| rate | Moody Corporate Bond Index Rate.  |
