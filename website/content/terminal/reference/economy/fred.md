---
title: fred
description: OpenBB Terminal Function
---

# fred

Query the FRED database and plot data based on the Series ID. [Source: FRED]

### Usage

```python
fred [-p PARAMETER] [-s START_DATE] [-e END_DATE] [-q QUERY]
```

---

## Parameters

| Name | Description | Default | Optional | Choices |
| ---- | ----------- | ------- | -------- | ------- |
| parameter | Series ID of the Macro Economic data from FRED |  | True | None |
| start_date | Starting date (YYYY-MM-DD) of data | None | True | None |
| end_date | Ending date (YYYY-MM-DD) of data | None | True | None |
| query | Query the FRED database to obtain Series IDs given the query search term. | None | True | None |


---

## Examples

```python
2022 Mar 15, 07:08 (🦋) /economy/ $ fred -q treasuries
                                                                    Search results for treasuries
┏━━━━━━━━━━━┳━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┳━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓
┃ Series ID ┃ Title                                           ┃ Description                                                                                         ┃
┡━━━━━━━━━━━╇━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━╇━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┩
│ T10Y2Y    │ 10-Year Treasury Constant Maturity Minus 2-Year │ Starting with the update on June 21, 2019, the Treasury bond data used in calculating interest rate │
│           │ Treasury Constant Maturity                      │ spreads is obtained directly from the U.S. Treasury Department (https://www.treasury.gov/resource-  │
│           │                                                 │ center/data-chart-center/interest-rates/Pages/TextView.aspx?data=yield).  Series is calculated as   │
│           │                                                 │ the spread between 10-Year Treasury Constant Maturity (BC_10YEAR) and 2-Year Treasury Constant      │
│           │                                                 │ Maturity (BC_2YEAR). Both underlying series are published at the U.S. Treasury Department           │
│           │                                                 │ (https://www.treasury.gov/resource-center/data-chart-center/interest-                               │
│           │                                                 │ rates/Pages/TextView.aspx?data=yield).                                                              │
├───────────┼─────────────────────────────────────────────────┼─────────────────────────────────────────────────────────────────────────────────────────────────────┤
│ T10Y2YM   │ 10-Year Treasury Constant Maturity Minus 2-Year │ Series is calculated as the spread between 10-Year Treasury Constant Maturity (BC_10YEARM) and      │
│           │ Treasury Constant Maturity                      │ 2-Year Treasury Constant Maturity (BC_2YEARM). Starting with the update on June 21, 2019, the       │
│           │                                                 │ Treasury bond data used in calculating interest rate spreads is obtained directly from the U.S.     │
│           │                                                 │ Treasury Department (https://www.treasury.gov/resource-center/data-chart-center/interest-           │
│           │                                                 │ rates/Pages/TextView.aspx?data=yield).                                                              │
├───────────┼─────────────────────────────────────────────────┼─────────────────────────────────────────────────────────────────────────────────────────────────────┤
│ DFII10    │ Market Yield on U.S. Treasury Securities at     │ For further information regarding treasury constant maturity data, please refer to the Board of     │
│           │ 10-Year Constant Maturity, Inflation-Indexed    │ Governors ( http://www.federalreserve.gov/releases/h15/current/h15.pdf) and the Treasury            │
│           │                                                 │ (http://www.treasury.gov/resource-center/data-chart-center/interest-rates/Pages/yieldmethod.aspx).  │
├───────────┼─────────────────────────────────────────────────┼─────────────────────────────────────────────────────────────────────────────────────────────────────┤
│ FII10     │ Market Yield on U.S. Treasury Securities at     │ For further information regarding treasury constant maturity data, please refer to                  │
│           │ 10-Year Constant Maturity, Inflation-Indexed    │ http://www.federalreserve.gov/releases/h15/current/h15.pdf and http://www.treasury.gov/resource-    │
│           │                                                 │ center/data-chart-center/interest-rates/Pages/yieldmethod.aspx.                                     │
├───────────┼─────────────────────────────────────────────────┼─────────────────────────────────────────────────────────────────────────────────────────────────────┤
│ WFII10    │ Market Yield on U.S. Treasury Securities at     │ For further information regarding treasury constant maturity data, please refer to                  │
│           │ 10-Year Constant Maturity, Inflation-Indexed    │ http://www.federalreserve.gov/releases/h15/current/h15.pdf and http://www.treasury.gov/resource-    │
│           │                                                 │ center/data-chart-center/interest-rates/Pages/yieldmethod.aspx.                                     │
└───────────┴─────────────────────────────────────────────────┴─────────────────────────────────────────────────────────────────────────────────────────────────────┘
```
![fred](https://user-images.githubusercontent.com/46355364/158575129-1d4b26de-8bd8-49b3-b1b9-e349afaf8a50.png)

---
