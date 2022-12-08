---
title: Portfolio Optimization
keywords: ["portfolio", "optimization", "mean variance", "risk parity", "black litterman", "mean risk",
"hierarchical clustering models"]
excerpt: "The Introduction to Portfolio Optimization within the Portfolio menu explains how to use various portfolio
optimization techniques and provides a brief description of its sub-menus"
geekdocCollapseSection: true
---

The Portfolio Optimization menu allows the user to apply advanced optimization techniques to a portfolio of any type and of any size. It does so by introducing a multitude of optimization techniques ranging from <a href="https://www.investopedia.com/terms/m/meanvariance-analysis.asp" target="_blank" rel="noreferrer noopener">mean-variance optimization</a> to <a href="https://www.investopedia.com/terms/r/risk-parity.asp" target="_blank" rel="noreferrer noopener">risk parity models</a> and <a href="https://www.investopedia.com/terms/c/cluster_analysis.asp" target="_blank" rel="noreferrer noopener">hierarchical clustering models</a>. By providing Excel templates, the user can make sense of the vast array of parameters that each command has. E.g. think of the historic period you wish to use or which of the more than 10 risk measures and covariance methods should be used? These are questions the templates make easier to answer.

### How to use

The portfolio optimization menu can be reached by visiting the `portfolio` menu and typing `po` (or alternatively, typing `/portfolio/po` from any location). This opens the following menu:

<img src="https://user-images.githubusercontent.com/46355364/171144243-dbdc09e8-609e-4dc3-abb8-8148405e7308.png"></img>

This menu requires the usage of the Excel templates to work properly. As there is a lot of complexity involved around these techniques, these templates allow the user to understand what values for each parameter are actually used and allow for an easy way to define the allocation.

For this there are two templates that need to be set:

- **OpenBB Parameters Template**: found in the OpenBBUserData directory within `~/OpenBBUserData/portfolio/parameters`
- **OpenBB Portfolio Template**: found in the OpenBBUserData directory within `~/OpenBBUserData/portfolio/allocation`

The OpenBBUserData directory is created automatically. See for more information [here](https://docs.openbb.co/terminal/quickstart/data).

#### OpenBB Parameters Template

This template provides the user with the ability to set define values for each parameter based on the optimization technique that is deployed. E.g. if you select `riskparity` for the `technique` parameter, you will notice that some parameters turn <span style={{color: "#BEBEBE"}}>grey</span>. This means that the parameter is irrelevant for the selected method.

The OpenBB Terminal does, however, allow the user to run any model despite the `technique` you selected. Therefore, if you are interested in running multiple models, consider removing the value for `technique`. Do note that this makes it more difficult to understand which values are used for which model.

<img src="https://user-images.githubusercontent.com/46355364/171144692-dd812efd-1e95-4a71-a93f-7ae8a480fe5d.png"></img>

Once you have defined the parameters, save the template and load it inside the terminal by using the <a href="/terminal/reference/portfolio/po/file/" target="_blank" rel="noreferrer noopener">file</a> command. If done correctly, the parameters file should show automatically after typing `file` and pressing SPACE. Then, by using the DOWN KEY (⌄) you can select the file by pressing ENTER (⏎) which will then be loaded into the terminal:

```
2022 May 02, 06:51 (🦋) /portfolio/po/ $ file OpenBB_Parameters_Template v1.0.0.xlsx
Parameters:
    historic_period         : 3y
    log_returns             : 0
    return_frequency        : d
    max_nan                 : 0.05
    threshold_value         : 0.3
    nan_fill_method         : time
    risk_free               : 0.003
    significance_level      : 0.05
    risk_measure            : MV
    target_return           : -1
    target_risk             : -1
    expected_return         : hist
    covariance              : hist
    smoothing_factor_ewma   : 0.94
    long_allocation         : 1
    short_allocation        : 0
```

#### OpenBB Portfolio Template

This template hands the user a format to work with it to define the portfolio. Here, categorization is applied based on asset class, sector, industry, country and currency. By using the dropdown menus within this Excel, you are able to apply the proper categorization. This is based on the same methodology as found in other areas of the terminal.

<img src="https://user-images.githubusercontent.com/46355364/171145061-cd618153-801c-4771-ba57-7ee0ab8c57e8.png"></img>

You can load in the portfolio template by using the <a href="/terminal/reference/portfolio/po/load" target="_blank" rel="noreferrer noopener">load</a> command:

```
2022 Apr 26, 01:35 (🦋) /portfolio/po/ $ load OpenBB_Portfolio_Template_v1.0.0.xlsx
2022 Apr 26, 02:15 (🦋) /portfolio/po/ $ show

Current Portfolios: None

Current Categories: ASSET_CLASS, SECTOR, INDUSTRY, COUNTRY, CURRENT_INVESTED_AMOUNT, CURRENCY
```

#### Performing optimization

Based on the parameters and allocation the user has set, the optimization process begins. What optimization technique is ideal depends entirely on the user's risk profile and objectives. As an illustration, <a href="https://www.investopedia.com/terms/r/risk-parity.asp" target="_blank" rel="noreferrer noopener">Risk Parity</a> is presented below via the <a href="/terminal/reference/portfolio/po/riskparity" target="_blank" rel="noreferrer noopener">riskparity</a> command:

```
2022 May 30, 05:47 (🦋) /portfolio/po/ $ riskparity
Optimization can take time. Please be patient...

 [3 Years] Risk parity portfolio based on risk budgeting approach
using volatility as risk measure


      Weights
┏━━━━━━━┳━━━━━━━━━━┓
┃       ┃ Value    ┃
┡━━━━━━━╇━━━━━━━━━━┩
│ AAPL  │   3.27 % │
├───────┼──────────┤
│ AMZN  │   3.81 % │
├───────┼──────────┤
│ APTV  │   2.17 % │
├───────┼──────────┤
│ ASML  │   2.48 % │
├───────┼──────────┤
│ BABA  │   3.42 % │
├───────┼──────────┤
│ GOOGL │   3.54 % │
├───────┼──────────┤
│ HYG   │   9.40 % │
├───────┼──────────┤
│ IYR   │   3.98 % │
├───────┼──────────┤
│ NKE   │   3.66 % │
├───────┼──────────┤
│ PEX   │   3.88 % │
├───────┼──────────┤
│ PSP   │   3.49 % │
├───────┼──────────┤
│ REZ   │   4.08 % │
├───────┼──────────┤
│ TIP   │  26.61 % │
├───────┼──────────┤
│ TLT   │  22.86 % │
├───────┼──────────┤
│ TSM   │   3.35 % │
└───────┴──────────┘

Annual (by 252) expected return: 10.03%
Annual (by √252) volatility: 11.62%
Sharpe ratio: 0.8373
```

To understand how this portfolio differs from the original portfolio, the <a href="/terminal/reference/portfolio/po/show" target="_blank" rel="noreferrer noopener">show</a> command can be used. This also shows the allocations to each asset class, sector, industry and currency. Using the optimized portfolio, this generates the following results:

```
2022 May 30, 05:47 (🦋) /portfolio/po/ $ show RP_0

Portfolio - RP_0

                            Category - Asset_Class
┏━━━━━┳━━━━━━━━━━━━━━━━┳━━━━━━━━━━━━━━━━━━━━━━━━━┳━━━━━━━━━━━━━━━━━┳━━━━━━━━━━┓
┃     ┃ Asset_Class    ┃ Current_Invested_Amount ┃ Current_Weights ┃ Value    ┃
┡━━━━━╇━━━━━━━━━━━━━━━━╇━━━━━━━━━━━━━━━━━━━━━━━━━╇━━━━━━━━━━━━━━━━━╇━━━━━━━━━━┩
│ USD │ FIXED INCOME   │             2,550,000 $ │         30.03 % │  58.87 % │
├─────┼────────────────┼─────────────────────────┼─────────────────┼──────────┤
│ USD │ PRIVATE EQUITY │               850,000 $ │         10.01 % │   7.37 % │
├─────┼────────────────┼─────────────────────────┼─────────────────┼──────────┤
│ USD │ PUBLIC EQUITY  │             4,242,000 $ │         49.95 % │  25.69 % │
├─────┼────────────────┼─────────────────────────┼─────────────────┼──────────┤
│ USD │ REAL ESTATE    │               850,000 $ │         10.01 % │   8.07 % │
├─────┼────────────────┼─────────────────────────┼─────────────────┼──────────┤
│ USD │ TOTAL USD      │             8,492,000 $ │        100.00 % │ 100.00 % │
└─────┴────────────────┴─────────────────────────┴─────────────────┴──────────┘



                              Category - Country
┏━━━━━┳━━━━━━━━━━━━━━━┳━━━━━━━━━━━━━━━━━━━━━━━━━┳━━━━━━━━━━━━━━━━━┳━━━━━━━━━━┓
┃     ┃ Country       ┃ Current_Invested_Amount ┃ Current_Weights ┃ Value    ┃
┡━━━━━╇━━━━━━━━━━━━━━━╇━━━━━━━━━━━━━━━━━━━━━━━━━╇━━━━━━━━━━━━━━━━━╇━━━━━━━━━━┩
│ USD │ CHINA         │               246,000 $ │          2.90 % │   3.42 % │
├─────┼───────────────┼─────────────────────────┼─────────────────┼──────────┤
│ USD │ NETHERLANDS   │               920,000 $ │         10.83 % │   2.48 % │
├─────┼───────────────┼─────────────────────────┼─────────────────┼──────────┤
│ USD │ TAIWAN        │               380,000 $ │          4.47 % │   3.35 % │
├─────┼───────────────┼─────────────────────────┼─────────────────┼──────────┤
│ USD │ UNITED STATES │             6,946,000 $ │         81.79 % │  90.76 % │
├─────┼───────────────┼─────────────────────────┼─────────────────┼──────────┤
│ USD │ TOTAL USD     │             8,492,000 $ │        100.00 % │ 100.00 % │
└─────┴───────────────┴─────────────────────────┴─────────────────┴──────────┘



                                   Category - Sector
┏━━━━━┳━━━━━━━━━━━━━━━━━━━━━━━━┳━━━━━━━━━━━━━━━━━━━━━━━━━┳━━━━━━━━━━━━━━━━━┳━━━━━━━━━━┓
┃     ┃ Sector                 ┃ Current_Invested_Amount ┃ Current_Weights ┃ Value    ┃
┡━━━━━╇━━━━━━━━━━━━━━━━━━━━━━━━╇━━━━━━━━━━━━━━━━━━━━━━━━━╇━━━━━━━━━━━━━━━━━╇━━━━━━━━━━┩
│ USD │ COMMUNICATION SERVICES │               636,000 $ │          7.49 % │   3.54 % │
├─────┼────────────────────────┼─────────────────────────┼─────────────────┼──────────┤
│ USD │ CONSUMER CYCLICAL      │             1,926,000 $ │         22.68 % │  13.06 % │
├─────┼────────────────────────┼─────────────────────────┼─────────────────┼──────────┤
│ USD │ CORPORATE BOND         │               810,000 $ │          9.54 % │   9.40 % │
├─────┼────────────────────────┼─────────────────────────┼─────────────────┼──────────┤
│ USD │ FINANCIAL              │               850,000 $ │         10.01 % │   7.37 % │
├─────┼────────────────────────┼─────────────────────────┼─────────────────┼──────────┤
│ USD │ GOVERNMENT BOND        │             1,740,000 $ │         20.49 % │  49.47 % │
├─────┼────────────────────────┼─────────────────────────┼─────────────────┼──────────┤
│ USD │ REAL ESTATE            │               850,000 $ │         10.01 % │   8.07 % │
├─────┼────────────────────────┼─────────────────────────┼─────────────────┼──────────┤
│ USD │ TECHNOLOGY             │             1,680,000 $ │         19.78 % │   9.09 % │
├─────┼────────────────────────┼─────────────────────────┼─────────────────┼──────────┤
│ USD │ TOTAL USD              │             8,492,000 $ │        100.00 % │ 100.00 % │
└─────┴────────────────────────┴─────────────────────────┴─────────────────┴──────────┘



                                            Category - Industry
┏━━━━━┳━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┳━━━━━━━━━━━━━━━━━━━━━━━━━┳━━━━━━━━━━━━━━━━━┳━━━━━━━━━━┓
┃     ┃ Industry                                   ┃ Current_Invested_Amount ┃ Current_Weights ┃ Value    ┃
┡━━━━━╇━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━╇━━━━━━━━━━━━━━━━━━━━━━━━━╇━━━━━━━━━━━━━━━━━╇━━━━━━━━━━┩
│ USD │ AUTO PARTS & EQUIPMENT                     │               429,000 $ │          5.05 % │   2.17 % │
├─────┼────────────────────────────────────────────┼─────────────────────────┼─────────────────┼──────────┤
│ USD │ FINANCIAL SERVICES                         │               850,000 $ │         10.01 % │   7.37 % │
├─────┼────────────────────────────────────────────┼─────────────────────────┼─────────────────┼──────────┤
│ USD │ FOOTWEAR & ACCESSORIES                     │               505,000 $ │          5.95 % │   3.66 % │
├─────┼────────────────────────────────────────────┼─────────────────────────┼─────────────────┼──────────┤
│ USD │ HIGH YIELD BOND                            │               810,000 $ │          9.54 % │   9.40 % │
├─────┼────────────────────────────────────────────┼─────────────────────────┼─────────────────┼──────────┤
│ USD │ INFLATION-PROTECTED BOND                   │               890,000 $ │         10.48 % │  26.61 % │
├─────┼────────────────────────────────────────────┼─────────────────────────┼─────────────────┼──────────┤
│ USD │ INTERACTIVE MEDIA & SERVICES               │               636,000 $ │          7.49 % │   3.54 % │
├─────┼────────────────────────────────────────────┼─────────────────────────┼─────────────────┼──────────┤
│ USD │ INTERNET & DIRECT MARKETING RETAIL         │               992,000 $ │         11.68 % │   7.23 % │
├─────┼────────────────────────────────────────────┼─────────────────────────┼─────────────────┼──────────┤
│ USD │ LONG GOVERNMENT                            │               850,000 $ │         10.01 % │  22.86 % │
├─────┼────────────────────────────────────────────┼─────────────────────────┼─────────────────┼──────────┤
│ USD │ RESIDENTIAL                                │               280,000 $ │          3.30 % │   4.08 % │
├─────┼────────────────────────────────────────────┼─────────────────────────┼─────────────────┼──────────┤
│ USD │ SEMICONDUCTORS                             │             1,300,000 $ │         15.31 % │   5.82 % │
├─────┼────────────────────────────────────────────┼─────────────────────────┼─────────────────┼──────────┤
│ USD │ TECHNOLOGY HARDWARE, STORAGE & PERIPHERALS │               380,000 $ │          4.47 % │   3.27 % │
├─────┼────────────────────────────────────────────┼─────────────────────────┼─────────────────┼──────────┤
│ USD │ TOTAL MARKET                               │               570,000 $ │          6.71 % │   3.98 % │
├─────┼────────────────────────────────────────────┼─────────────────────────┼─────────────────┼──────────┤
│ USD │ TOTAL USD                                  │             8,492,000 $ │        100.00 % │ 100.00 % │
└─────┴────────────────────────────────────────────┴─────────────────────────┴─────────────────┴──────────┘
```

It is possible to use the commands without loading in the parameters template or by using the parameters template but changing some arguments directly into the terminal. For example, using the same method as described above, the risk measure is changed to <a href="https://www.investopedia.com/terms/c/conditional_value_at_risk.asp" target="_blank" rel="noreferrer noopener">Conditional Value at Risk (CVaR)</a> and the used historic period is increased to 10 years (keeping all other parameters unchanged):

```
2022 May 30, 05:47 (🦋) /portfolio/po/ $ riskparity -rm CVaR -p 10y
Optimization can take time. Please be patient...

 [10 Years] Risk parity portfolio based on risk budgeting approach
using conditional value at risk (CVaR) as risk measure


      Weights
┏━━━━━━━┳━━━━━━━━━━┓
┃       ┃ Value    ┃
┡━━━━━━━╇━━━━━━━━━━┩
│ AAPL  │   3.78 % │
├───────┼──────────┤
│ AMZN  │   3.55 % │
├───────┼──────────┤
│ APTV  │   3.06 % │
├───────┼──────────┤
│ ASML  │   3.11 % │
├───────┼──────────┤
│ GOOGL │   3.80 % │
├───────┼──────────┤
│ HYG   │  11.68 % │
├───────┼──────────┤
│ IYR   │   4.68 % │
├───────┼──────────┤
│ NKE   │   4.31 % │
├───────┼──────────┤
│ PSP   │   4.54 % │
├───────┼──────────┤
│ REZ   │   4.91 % │
├───────┼──────────┤
│ TIP   │  29.23 % │
├───────┼──────────┤
│ TLT   │  19.69 % │
├───────┼──────────┤
│ TSM   │   3.66 % │
└───────┴──────────┘

Annual (by 252) expected return: 9.70%
Annual (by √252) volatility: 8.34%
Sharpe ratio: 1.1275
Annual (by √252) conditional value at risk (CVaR) : 19.84%
Return / conditional value at risk (CVaR) ratio: 0.4738
```

## Examples

To demonstrate the capabilities of the Portfolio Optimization menu, the entire <a href="https://www.investopedia.com/terms/s/sp500.asp" target="_blank" rel="noreferrer noopener">S&P 500 index</a> (as of 30th of May 2022) is used and optimized and analysed in a variety of ways. Starting by loading in the dataset, which is visible when you type `load` as it resides in the same directory as the earlier mentioned template:

<img src="https://user-images.githubusercontent.com/46355364/171145309-8419bc2e-12bd-49d5-8c19-e0f80097d898.png"></img>

It is possible to load the parameters template here but this is not necessary as each parameter has a default value set regardless. However, because the Excel file provides a more structured way of presenting the choices, the template is loaded in:

```
2022 May 30, 06:15 (🦋) /portfolio/po/ $ file OpenBB_Parameters_Template_v1.0.0.xlsx
Parameters:
    historic_period         : 3y
    log_returns             : 0
    return_frequency        : d
    max_nan                 : 0.05
    threshold_value         : 0.3
    nan_fill_method         : time
    risk_free               : 0.003
    significance_level      : 0.05
    risk_measure            : MV
    target_return           : -1
    target_risk             : -1
    expected_return         : hist
    covariance              : hist
    smoothing_factor_ewma   : 0.94
    long_allocation         : 1
    short_allocation        : 0
```

Then, the <a href="https://jpm.pm-research.com/content/42/4/59.short" target="_blank" rel="noreferrer noopener">Hierarchical Risk Parity</a> technique is applied by running the <a href="/terminal/reference/portfolio/po/hrp/" target="_blank" rel="noreferrer noopener">hrp</a> command. This results in the following (the result is edited, as it would show 500 tickers, to prevent flooding this page):

```
2022 May 30, 06:22 (🦋) /portfolio/po/ $ hrp
Optimization can take time. Please be patient...

 [3 Years] Hierarchical risk parity portfolio using pearson codependence,
single linkage and volatility as risk measure


      Weights
┏━━━━━━━┳━━━━━━━━━━┓
┃       ┃ Value    ┃
┡━━━━━━━╇━━━━━━━━━━┩
│ A     │   0.23 % │
├───────┼──────────┤
│ AAL   │   0.04 % │
├───────┼──────────┤
│ AAP   │   0.21 % │
├───────┼──────────┤
│ AAPL  │   0.15 % │
├───────┼──────────┤
│ ABBV  │   0.41 % │
├───────┼──────────┤
│ ABC   │   0.18 % │
├───────┼──────────┤
<continues>

Annual (by 252) expected return: 19.65%
Annual (by √252) volatility: 21.64%
Sharpe ratio: 0.8943
```

This optimization process is then compared with the current holdings. To keep things manageable, only the sector allocations are compared between the unoptimized and optimized portfolio which is done with the <a href="/terminal/reference/portfolio/po/show/" target="_blank" rel="noreferrer noopener">show</a> command:

```
2022 May 31, 03:31 (🦋) /portfolio/po/ $ show HRP_0 -ct SECTOR

                                   Category - Sector
┏━━━━━┳━━━━━━━━━━━━━━━━━━━━━━━━┳━━━━━━━━━━━━━━━━━━━━━━━━━┳━━━━━━━━━━━━━━━━━┳━━━━━━━━━━┓
┃     ┃ Sector                 ┃ Current_Invested_Amount ┃ Current_Weights ┃ Value    ┃
┡━━━━━╇━━━━━━━━━━━━━━━━━━━━━━━━╇━━━━━━━━━━━━━━━━━━━━━━━━━╇━━━━━━━━━━━━━━━━━╇━━━━━━━━━━┩
│ USD │ COMMUNICATION SERVICES │            14,934,743 $ │          5.89 % │   6.07 % │
├─────┼────────────────────────┼─────────────────────────┼─────────────────┼──────────┤
│ USD │ CONSUMER DISCRETIONARY │            31,210,119 $ │         12.31 % │   9.58 % │
├─────┼────────────────────────┼─────────────────────────┼─────────────────┼──────────┤
│ USD │ CONSUMER STAPLES       │            15,957,911 $ │          6.29 % │  11.93 % │
├─────┼────────────────────────┼─────────────────────────┼─────────────────┼──────────┤
│ USD │ ENERGY                 │             9,582,634 $ │          3.78 % │   1.97 % │
├─────┼────────────────────────┼─────────────────────────┼─────────────────┼──────────┤
│ USD │ FINANCIALS             │            30,165,029 $ │         11.89 % │   8.93 % │
├─────┼────────────────────────┼─────────────────────────┼─────────────────┼──────────┤
│ USD │ HEALTH CARE            │            31,802,164 $ │         12.54 % │  17.35 % │
├─────┼────────────────────────┼─────────────────────────┼─────────────────┼──────────┤
│ USD │ INDUSTRIALS            │            38,183,932 $ │         15.06 % │  14.04 % │
├─────┼────────────────────────┼─────────────────────────┼─────────────────┼──────────┤
│ USD │ INFORMATION TECHNOLOGY │            37,669,554 $ │         14.85 % │  12.95 % │
├─────┼────────────────────────┼─────────────────────────┼─────────────────┼──────────┤
│ USD │ MATERIALS              │            14,155,430 $ │          5.58 % │   5.49 % │
├─────┼────────────────────────┼─────────────────────────┼─────────────────┼──────────┤
│ USD │ REAL ESTATE            │            17,137,343 $ │          6.76 % │   4.82 % │
├─────┼────────────────────────┼─────────────────────────┼─────────────────┼──────────┤
│ USD │ UTILITIES              │            12,808,749 $ │          5.05 % │   6.87 % │
├─────┼────────────────────────┼─────────────────────────┼─────────────────┼──────────┤
│ USD │ TOTAL USD              │           253,607,608 $ │        100.00 % │ 100.00 % │
└─────┴────────────────────────┴─────────────────────────┴─────────────────┴──────────┘
```

This table shows how the portfolio changed and how much is allocated to each sector. It is possible to delve further into these findings with the <a href="/terminal/reference/portfolio/po/plot/" target="_blank" rel="noreferrer noopener">plot</a> command. This gives the ability to visually depict allocations, e.g. below the sector allocation is visually depicted.

```
2022 May 31, 03:39 (🦋) /portfolio/po/ $ plot HRP_0 -ct SECTOR -pi
```

<img alt="Sectors Pie Chart" src="https://user-images.githubusercontent.com/46355364/171145554-327ab405-dfb1-449e-a837-44ee03d2564f.png"></img>

Further analysis can be done by looking at the portfolio's returns <a href="https://www.investopedia.com/terms/h/histogram.asp" target="_blank" rel="noreferrer noopener">histogram</a> which also includes a variety of risk measures as well as the portfolio's drawdowns.

````
2022 May 31, 03:39 (🦋) /portfolio/po/ $ plot HRP_0 -ct SECTOR -hi -dd
````

<img alt="Portfokio Returns Histogram" src="https://user-images.githubusercontent.com/46355364/171145848-5a3f5333-6b7f-4d7a-a96e-0859adb1ce78.png"></img>
<img alt="Portfolio Drawdowns" src="https://user-images.githubusercontent.com/46355364/171145983-2d2c1c2e-67d2-4839-b43a-51bd22332de8.png"></img>

Next to that, to delve deeper in the underlying conclusions the HRP method has drawn. Here, a closer look can be given to the assets cluster map, which links certain categories to each other. The linkage process is done per asset basis but here it is grouped per sector. Based on these results, the user can identify whether the optimization techniques also logically makes sense.

````

2022 May 31, 03:45 (🦋) /portfolio/po/ $ plot HRP_0 -ct SECTOR -rc -he

````

<img alt="Heatmap with Linkage Method" src="https://user-images.githubusercontent.com/46355364/171146147-1b30a5f7-c488-4fe1-93e0-8266945ca4e7.png"></img>
<img alt="Risk Contributions" src="https://user-images.githubusercontent.com/46355364/171146286-84d268e5-ac77-4d50-bddb-9a0859ac896b.png"></img>
