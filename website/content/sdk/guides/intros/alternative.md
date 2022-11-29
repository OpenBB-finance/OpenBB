---
title: Alternative
keywords: ['alts']
excerpt: "Alternative Menus in the OpenBB Terminal"

---

The Alternative module provides programmatic access to the commands from within the OpenBB Terminal. Import the OpenBB SDK module, and then access the functions similarly to how the Terminal menus are navigated. The code completion will be activated upon entering `.`, after, `openbb.alt`

## How to Use
​
The examples provided below will assume that the following import block is included at the beginning of the Python script or Notebook file:
​
```python
from openbb_terminal.sdk import openbb
import pandas as pd
```

A brief description below highlights the main Functions and Modules available in the Alternative SDK

### OSS

|Path |Type | Description |
| :--------- | :---------: | ----------: |
|openbb.alt.oss.top |Function |Get top repositories |
|openbb.alt.oss.search |Function |Search repositories |
|openbb.alt.oss.history |Function |Display a repo star history |
|openbb.alt.oss.ross |Function |Startups from ross index |
|openbb.alt.oss.github_data |Function |Get repository stats |
|openbb.alt.oss.summary |Function |Get repository summary |
### Covid

|Path |Type | Description |
| :--------- | :---------: | ----------: |
|openbb.alt.covid.global_deaths |Function |historical deaths for given country |
|openbb.alt.covid.slopes |Function |Load cases and find slope over period |
|openbb.alt.covid.stat |Function |Show historical cases and deaths by country |
|openbb.alt.covid.global_cases |Function |historical cases for given country |
|openbb.alt.covid.ov |Function | overview historical cases and deaths by country |


Alteratively you can print the contents of the Alternative SDK with:
​
```python
help(openbb.alt.covid)
help(openbb.alt.oss)
```

## Examples - OSS


:::note

To use some of the OSS SDK commands you will need a GitHub API key - you can get one [here](https://docs.github.com/en/authentication/keeping-your-account-and-data-secure/creating-a-personal-access-token)


:::
### alt.oss.top
​
The alt.oss.top SDK command lets you display top repositories - You can pass different parameters like `sortby` `categories` and `limit` to enhance the output.
​
```python
summary = pd.DataFrame.from_dict(openbb.alt.oss.top(sortby='stars', categories='finance', limit=10))
print(summary[['full_name', 'open_issues', 'stargazers_count']])
```

|full_name |open_issues |stargazers_count|
| :--------- | :---------: | ----------: |
|                      vnpy/vnpy    |       8      |      19487|
|  OpenBB-finance/OpenBBTerminal    |     149      |      17645|
|                    plotly/dash    |     707      |      17645|
|                 waditu/tushare    |     556      |      11829|
|    wilsonfreitas/awesome-quant    |       9      |      10874|
|                 microsoft/qlib    |     232      |       9926|
|        firefly-iii/firefly-iii    |     103      |       9228|
|            ranaroussi/yfinance    |     441      |       7938|
|                  mrjbq7/ta-lib    |     181      |       7157|
|              QuantConnect/Lean    |     417      |       6773|

### alt.oss.summary

The alt.oss.summary SDK command gets you some info on a reposity - You just pass the repo path and can see all kinds of interesting information.

```python
summary = pd.DataFrame.from_dict(openbb.alt.oss.summary(repo="openbb-finance/openbbterminal"))
print(summary)
```

|Metric |Value |
| :--------- | ---------: |
| Name       | OpenBBTerminal |
| Owner       | OpenBB-finance |
| Creation Date       | 2020-12-20 |
| Last Update       | 2022-11-17 |
| Topics       | artificial-intelligence, crypto, cryptocurrenc... |
| Stars       | 17643 |
| Forks       | 1849 |
| Open Issues       | 152 |
| Language       | Python |
| License       | MIT License |
| Releases       |  10 |
| Last Release Downloads       | 10201 |
​
## Examples - Covid

### alt.covid.global_deaths

The global_deaths command lets you check quickly the global deaths for any `country`
​
```python
global_deaths = pd.DataFrame.from_dict(openbb.alt.covid.global_deaths(country="US"))
print(global_deaths)
```

|Date |US |
| :--------- | ---------: |
| 2020-01-23  |  0.0|
| 2020-01-24  |  0.0|
| 2020-01-25  |  0.0|
| 2020-01-26  |  0.0|
| 2020-01-27  |  0.0|
| ...         |  ...|
| 2022-11-12 | -40.0|
| 2022-11-13 |   1.0|
| 2022-11-14 | 216.0|
| 2022-11-15 | 387.0|
| 2022-11-16 | 825.0|

### alt.covid.slopes

The slopes command lets you check the slopes per country

```python
covid_slopes = pd.DataFrame.from_dict(openbb.alt.covid.slopes())
print(covid_slopes)
```
|Country |Slope |
| :--------- | ---------: |
|Japan      |      52199.941713|
|Korea, South  |   42252.945717|
|Germany       |   40376.811123|
|US            |   38365.586207|
|Taiwan*      |    28677.574861|
|France      |     24898.053393|
|Italy       |     20608.297664|
|Greece      |      7841.223359|
|Australia    |     6222.661846|
|Russia       |     5837.264739|
|Chile        |     5792.311457|
|Brazil       |     5605.621802|
|United Kingdom  |  4755.022692|
|Singapore     |    3867.323471|
|Switzerland    |   3393.054950|
|Malaysia      |    3154.148387|
|... | ... |


You can pass `days_back` `limit` and `ascend` to further drill down in your data.

```python
covid_slopes_params = pd.DataFrame.from_dict(
    openbb.alt.covid.slopes(days_back=30, limit=10, ascend=True)
)
print(covid_slopes_params)
```

|Country |Slope |
| :--------- | ---------: |
| Colombia  |  -9917.200222|
| Iran     |   -4000.273415|
| Slovakia |   -3553.934372|
| Poland   |    -563.439600|
| Lebanon  |    -364.833815|
| Bangladesh|   -175.475640|
| Albania   |    -96.862736|
| Bulgaria  |    -39.990656|
| Turkey    |    -31.636263|
| Belarus  |     -21.939043|
