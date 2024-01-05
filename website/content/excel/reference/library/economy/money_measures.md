<!-- markdownlint-disable MD041 -->

Money Measures.

## Syntax

```excel wordwrap
=OBB.ECONOMY.MONEY_MEASURES([provider];[start_date];[end_date];[adjusted])
```

### Example

```excel wordwrap
=OBB.ECONOMY.MONEY_MEASURES()
```

---

## Parameters

| Name | Type | Description | Optional |
| ---- | ---- | ----------- | -------- |
| provider | Text | Options: federal_reserve, defaults to federal_reserve. | True |
| start_date | Text | Start date of the data, in YYYY-MM-DD format. | True |
| end_date | Text | End date of the data, in YYYY-MM-DD format. | True |
| adjusted | Boolean | Whether to return seasonally adjusted data. | True |

---

## Return Data

| Name | Description |
| ---- | ----------- |
| month | The date of the data.  |
| M1 | Value of the M1 money supply in billions.  |
| M2 | Value of the M2 money supply in billions.  |
| currency | Value of currency in circulation in billions.  |
| demand_deposits | Value of demand deposits in billions.  |
| retail_money_market_funds | Value of retail money market funds in billions.  |
| other_liquid_deposits | Value of other liquid deposits in billions.  |
| small_denomination_time_deposits | Value of small denomination time deposits in billions.  |
