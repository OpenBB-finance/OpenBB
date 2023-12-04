---
title: ecb
description: Learn about the key interest rates set by the European Central Bank (ECB)
  for the Euro area. Explore the Python API for accessing European Central Bank interest
  rate data and understand the available parameters to customize your queries.
keywords: 
- European Central Bank interest rates
- ECB key interest rates
- ECB refinancing operations
- deposit facility rate
- marginal lending facility rate
- Python OBB fixed income API
- start date parameter
- end date parameter
- interest rate type parameter
- provider parameter
- European Central Bank Interest Rates data
- European Central Bank Interest Rates API
---

<!-- markdownlint-disable MD041 -->

European Central Bank Interest Rates.  The Governing Council of the ECB sets the key interest rates for the euro area:  - The interest rate on the main refinancing operations (MRO), which provide the bulk of liquidity to the banking system. - The rate on the deposit facility, which banks may use to make overnight deposits with the Eurosystem. - The rate on the marginal lending facility, which offers overnight credit to banks from the Eurosystem.

## Syntax

```excel wordwrap
=OBB.FIXEDINCOME.RATE.ECB(required;[optional])
```

---

## Parameters

| Name | Type | Description | Optional |
| ---- | ---- | ----------- | -------- |
| provider | Text | Options: fred | True |
| start_date | Text | Start date of the data, in YYYY-MM-DD format. | True |
| end_date | Text | End date of the data, in YYYY-MM-DD format. | True |
| interest_rate_type | Text | The type of interest rate. | True |

---

## Return Data

| Name | Description |
| ---- | ----------- |
| date | The date of the data.  |
| rate | European Central Bank Interest Rate.  |
