---
title: EMPLOYEE_COUNT
description: Learn how to retrieve historical employee count data using the Python
  API. Understand the parameters, returns, and data structure for the OBB.equity.fundamental.employee_count
  method.
keywords: 
- historical employees
- employee count
- Python API
- data retrieval
- symbol
- provider
- warnings
- chart object
- metadata
- data
- CIK
- acceptance time
- period of report
- company name
- form type
- filing date
- source URL
---

<!-- markdownlint-disable MD041 -->

Historical Employees. Historical number of employees.

## Syntax

```excel wordwrap
=OBB.EQUITY.FUNDAMENTAL.EMPLOYEE_COUNT(symbol;[provider])
```

### Example

```excel wordwrap
=OBB.EQUITY.FUNDAMENTAL.EMPLOYEE_COUNT("AAPL")
```

---

## Parameters

| Name | Type | Description | Required |
| ---- | ---- | ----------- | -------- |
| **symbol** | **Text** | **Symbol to get data for.** | **True** |
| provider | Text | Options: fmp, defaults to fmp. | False |

---

## Return Data

| Name | Description |
| ---- | ----------- |
| symbol | Symbol representing the entity requested in the data.  |
| cik | Central Index Key (CIK) for the requested entity.  |
| acceptance_time | Time of acceptance of the company employee.  |
| period_of_report | Date of reporting of the company employee.  |
| company_name | Registered name of the company to retrieve the historical employees of.  |
| form_type | Form type of the company employee.  |
| filing_date | Filing date of the company employee  |
| employee_count | Count of employees of the company.  |
| source | Source URL which retrieves this data for the company.  |
