---
title: share_statistics
description: Learn how to retrieve and analyze share statistics for a given company
  using the obb.equity.ownership.share_statistics API endpoint. This documentation
  provides details on the parameters, return values, and data structure.
keywords: 
- share statistics
- company statistics
- equity ownership
- symbol
- provider
- data
- free float
- float shares
- outstanding shares
- source
---

<!-- markdownlint-disable MD041 -->

Share Statistics. Share statistics for a given company.

## Syntax

```excel wordwrap
=OBB.EQUITY.OWNERSHIP.SHARE_STATISTICS(required;[optional])
```

---

## Parameters

| Name | Type | Description | Optional |
| ---- | ---- | ----------- | -------- |
| symbol | Text | Symbol to get data for. | False |
| provider | Text | Options: fmp, intrinio | True |

---

## Return Data

| Name | Description |
| ---- | ----------- |
| symbol | Symbol representing the entity requested in the data.  |
| date | The date of the data.  |
| free_float | Percentage of unrestricted shares of a publicly-traded company.  |
| float_shares | Number of shares available for trading by the general public.  |
| outstanding_shares | Total number of shares of a publicly-traded company.  |
| source | Source of the received data.  |
| adjusted_outstanding_shares | Total number of shares of a publicly-traded company, adjusted for splits. (provider: intrinio) |
| public_float | Aggregate market value of the shares of a publicly-traded company. (provider: intrinio) |
