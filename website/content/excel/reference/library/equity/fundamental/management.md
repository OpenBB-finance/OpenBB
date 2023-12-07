---
title: management
description: Learn about key executives for a company and how to retrieve their data
  using the `obb.equity.fundamental.management` function. Get details such as designation,
  name, pay, currency, gender, birth year, and title since.
keywords: 
- key executives
- company executives
- symbol
- data
- designation
- name
- pay
- currency
- gender
- birth year
- title since
---

<!-- markdownlint-disable MD041 -->

Key Executives. Key executives for a given company.

## Syntax

```excel wordwrap
=OBB.EQUITY.FUNDAMENTAL.MANAGEMENT(required;[optional])
```

---

## Parameters

| Name | Type | Description | Optional |
| ---- | ---- | ----------- | -------- |
| symbol | Text | Symbol to get data for. | False |
| provider | Text | Options: fmp | True |

---

## Return Data

| Name | Description |
| ---- | ----------- |
| title | Designation of the key executive.  |
| name | Name of the key executive.  |
| pay | Pay of the key executive.  |
| currency_pay | Currency of the pay.  |
| gender | Gender of the key executive.  |
| year_born | Birth year of the key executive.  |
| title_since | Date the tile was held since.  |
