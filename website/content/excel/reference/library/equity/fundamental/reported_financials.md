<!-- markdownlint-disable MD041 -->

Financial statements, as-reported.

## Syntax

```excel wordwrap
=OBB.EQUITY.FUNDAMENTAL.REPORTED_FINANCIALS( symbol; [provider]; [period]; [statement_type]; [limit]; [fiscal_year] )
```

---

## Example

```excel wordwrap
=OBB.EQUITY.FUNDAMENTAL.REPORTED_FINANCIALS("AAPL")
```

---

## Parameters

| Name | Type | Description | Optional |
| ---- | ---- | ----------- | -------- |
| **symbol** | **Text** | **Symbol to get data for.** | **False** |
| provider | Text | Options: intrinio, defaults to intrinio. | True |
| period | Text | Time period of the data to return. | True |
| statement_type | Text | The type of financial statement - i.e, balance, income, cash. | True |
| limit | Number | The number of data entries to return. Although the response object contains multiple results, because of the variance in the fields, year-to-year and quarter-to-quarter, it is recommended to view results in small chunks. | True |
| fiscal_year | Number | The specific fiscal year.  Reports do not go beyond 2008. (provider: intrinio) | True |

---

## Return Data

| Name | Description |
| ---- | ----------- |
| period_ending | The ending date of the reporting period.  |
| fiscal_period | The fiscal period of the report (e.g. FY, Q1, etc.).  |
| fiscal_year | The fiscal year of the fiscal period.  |
