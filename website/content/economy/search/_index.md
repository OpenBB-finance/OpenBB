```
usage: search [-s SERIES_TERM] [-n NUM] [-h]
```

Print series notes when searching for series. https://fred.stlouisfed.org

```
optional arguments:
  -s SERIES_TERM, --series SERIES_TERM
                        Search for this series term. (default: None)
  -n NUM, --num NUM     Maximum number of series notes to display. (default: 5)
  -h, --help            show this help message (default: False)
```
search household
```
(✨) (economy)> search household
UNRATE
------
The unemployment rate represents the number of unemployed as a percentage of the labor force. Labor force data are restricted to people 16 years of age and older, who currently reside in 1 of the 50 states or the District of Columbia, who do not reside in institutions (e.g., penal and mental facilities, homes for the aged), and who are not on active duty in the Armed Forces.

This rate is also defined as the U-3 measure of labor underutilization.

The series comes from the 'Current Population Survey (Household Survey)'

The source code is: LNS14000000

CIVPART
-------
The series comes from the 'Current Population Survey (Household Survey)'

The source code is: LNS11300000

MEHOINUSA672N
-------------
Household data are collected as of March.

As stated in the Census's Source and Accuracy of Estimates for Income, Poverty, and Health Insurance Coverage in the United States: 2011 (http://www.census.gov/hhes/www/p60_243sa.pdf).

Estimation of Median Incomes. The Census Bureau has changed the methodology for computing median income over time. The Census Bureau has computed medians using either Pareto interpolation or linear interpolation. Currently, we are using linear interpolation to estimate all medians. Pareto interpolation assumes a decreasing density of population within an income interval, whereas linear interpolation assumes a constant density of population within an income interval. The Census Bureau calculated estimates of median income and associated standard errors for 1979 through 1987 using Pareto interpolation if the estimate was larger than $20,000 for people or $40,000 for families and households. This is because the width of the income interval containing the estimate is greater than $2,500.

We calculated estimates of median income and associated standard errors for 1976, 1977, and 1978 using Pareto interpolation if the estimate was larger than $12,000 for people or $18,000 for families and households. This is because the width of the income interval containing the estimate is greater than $1,000. All other estimates of median income and associated standard errors for 1976 through 2011 (2012 ASEC) and almost all of the estimates of median income and associated standard errors for 1975 and earlier were calculated using linear interpolation.

Thus, use caution when comparing median incomes above $12,000 for people or $18,000 for families and households for different years. Median incomes below those levels are more comparable from year to year since they have always been calculated using linear interpolation. For an indication of the comparability of medians calculated using Pareto interpolation with medians calculated using linear interpolation, see Series P-60, Number 114, (https://www2.census.gov/prod2/popscan/p60-114.pdf) Money Income in 1976 of Families and Persons in the United States.

TDSP
----
The Household Debt Service Ratio (DSR) (https://fred.stlouisfed.org/series/TDSP) is the ratio of total required household debt payments to total disposable income.

The DSR is divided into two parts. The Mortgage DSR (MDSP) (https://fred.stlouisfed.org/series/MDSP) is total quarterly required mortgage payments divided by total quarterly disposable personal income. The Consumer DSR (CDSP) (https://fred.stlouisfed.org/series/CDSP) is total quarterly scheduled consumer debt payments divided by total quarterly disposable personal income. The Mortgage DSR and the Consumer DSR sum to the DSR.

For more information, please visit the Board of Governors (https://www.federalreserve.gov/releases/housedebt/about.htm).

LNS14000006
-----------
The series comes from the 'Current Population Survey (Household Survey)'

The source code is: LNS14000006
```
