---
title: Portfolio Optimization
keywords: [portfolio, attribution, optimization, pnl, benchmark, return, volatility, metrics, broker, integration, report, how to, example, mean variance, risk parity, hierarchical cluster]
description: A brief introduction and explanation of the Portfolio Optimization menu. It allows the user to apply advanced optimization techniques to a portfolio of any type and of any size.
---

import HeadTitle from '@site/src/components/General/HeadTitle.tsx';

<HeadTitle title="Portfolio Optimization - Terminal | OpenBB Docs" />

The Portfolio Optimization menu allows the user to apply advanced optimization techniques to a portfolio of any type and of any size. It does so by introducing a multitude of optimization techniques ranging from <a href="https://www.investopedia.com/terms/m/meanvariance-analysis.asp" target="_blank" rel="noreferrer noopener">mean-variance optimization</a> to <a href="https://www.investopedia.com/terms/r/risk-parity.asp" target="_blank" rel="noreferrer noopener">risk parity models</a> and <a href="https://www.investopedia.com/terms/c/cluster_analysis.asp" target="_blank" rel="noreferrer noopener">hierarchical clustering models</a>. By providing Excel templates, the user can make sense of the vast array of parameters that each command has. E.g. think of the historic period you wish to use or which of the more than 10 risk measures and covariance methods should be used? These are questions the templates make easier to answer.

### How to use

The portfolio optimization menu can be reached by visiting the `portfolio` menu and typing `po` (or alternatively, typing `/portfolio/po` from any location). This opens the following menu:

<img width="800" alt="image" src="https://user-images.githubusercontent.com/46355364/218996021-63d4b1f9-efad-4303-bdde-7de3115157a7.png"></img>

The first step in using this menu is loading a portfolio with <a href="/terminal/reference/portfolio/po/load" target="_blank" rel="noreferrer noopener">load</a>. Within this guide, we provide an example file when running `load --example` which will be used to explain the functionality through the guide.

:::note If you wish to load in your own Excel allocation file, please follow the following steps:
1. Download the Excel file that can be used as a template [here](https://www.dropbox.com/s/wp1lcq86exyngjy/allocation_example.xlsx?dl=0).
2. Move the file inside the `portfolio/allocation` folder within the [OpenBBUserData](https://docs.openbb.co/terminal/usage/guides/data) folder and, optionally, adjust the name to your liking.
3. Open the Excel file and remove, edit or add to the values as you desire (e.g. your own allocation). This is the default template that is also loaded in with `load --example`.
4. Open up the OpenBB Terminal, go to `portfolio/po` and type `load --file`. Your Excel file should then be one of the options.
:::

Furthermore, given the amount of options you can choose from in each command and giving the complexity of the topic, we also provide a parameter file (both .xlsx and .ini to adjust parameters in a user-friendly way).

:::note If you wish to load in your own Excel or ini parameter file, please follow the following steps:
1. Download the file that can be used as a template: [xlsx](https://www.dropbox.com/s/qfhd7ntj7mlwsuc/parameters_template.xlsx?dl=0) (recommended) or [ini](https://www.dropbox.com/s/3ehwg3hiwm89hgo/parameters_template.ini?dl=0) (advanced).
2. Move the file inside the `portfolio/optimization` folder within the [OpenBBUserData](https://docs.openbb.co/terminal/usage/guides/data) folder and, optionally, adjust the name to your liking.
3. Open the file and set parameters as you wish.
4. Open up the OpenBB Terminal, go to `portfolio/po` and type `file --file`. The file should then be one of the options.
:::

Find more information about these two templates below.

#### OpenBB Portfolio Template

This template hands the user a format to work with it to define the portfolio. Here, categorization is applied based on asset class, sector, industry, country and currency. By using the dropdown menus within this Excel, you are able to apply the proper categorization. This is based on the same methodology as found in other areas of the terminal.

<img src="https://user-images.githubusercontent.com/46355364/171145061-cd618153-801c-4771-ba57-7ee0ab8c57e8.png"></img>

You can load in the portfolio template by using the <a href="/terminal/reference/portfolio/po/load" target="_blank" rel="noreferrer noopener">load</a> command or use `load --example` to obtain an example allocation:

```
(🦋) /portfolio/po/ $ load --file allocation_example.xlsx
(🦋) /portfolio/po/ $ show

Current Portfolios: None

Current Categories: ASSET_CLASS, SECTOR, INDUSTRY, COUNTRY, CURRENT_INVESTED_AMOUNT, CURRENCY
```

#### OpenBB Parameters Template

This template provides the user with the ability to set define values for each parameter based on the optimization technique that is deployed. E.g. if you select `riskparity` for the `technique` parameter, you will notice that some parameters turn <span style={{color: "#BEBEBE"}}>grey</span>. This means that the parameter is irrelevant for the selected method.

The OpenBB Terminal does, however, allow the user to run any model despite the `technique` you selected. Therefore, if you are interested in running multiple models, consider removing the value for `technique`. Do note that this makes it more difficult to understand which values are used for which model.

<img src="https://user-images.githubusercontent.com/46355364/171144692-dd812efd-1e95-4a71-a93f-7ae8a480fe5d.png"></img>

Once you have defined the parameters, save the template and load it inside the terminal by using the <a href="/terminal/reference/portfolio/po/file/" target="_blank" rel="noreferrer noopener">file</a> command. If done correctly, the parameters file should show automatically after typing `file` and pressing SPACE. Then, by using the DOWN KEY (⌄) you can select the file by pressing ENTER (⏎) which will then be loaded into the terminal:

```
(🦋) /portfolio/po/ $ file parameters_template.xlsx
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

#### Performing optimization

Based on the parameters and allocation the user has set, the optimization process begins. What optimization technique is ideal depends entirely on the user's risk profile and objectives. As an illustration, <a href="https://www.investopedia.com/terms/r/risk-parity.asp" target="_blank" rel="noreferrer noopener">Risk Parity</a> is presented below via the <a href="/terminal/reference/portfolio/po/riskparity" target="_blank" rel="noreferrer noopener">riskparity</a> command.

First of all, we load in the example portfolio as follows:

```
(🦋) /portfolio/po/ $ load --example

Loading an example, please type `about` to learn how to create your own Portfolio Optimization Excel sheet.


(🦋) /portfolio/po/ $ ?

╭────────────────────────────────────────────────────────────────────────── Portfolio - Portfolio Optimization ───────────────────────────────────────────────────────────────────────────╮
│                                                                                                                                                                                         │
│     load               load tickers and categories from .xlsx or .csv file                                                                                                              │
│                                                                                                                                                                                         │
│ Portfolio loaded: OpenBB Example Portfolio                                                                                                                                              │
│                                                                                                                                                                                         │
│ Tickers: AAPL, AMZN, APTV, ASML, BABA, GOOGL, HYG, IYR, NKE, PEX, PSP, REZ, TIP, TLT, TSM                                                                                               │
│ Categories: ASSET_CLASS, SECTOR, INDUSTRY, COUNTRY, CURRENCY                                                                                                                            |
<continues>
```

```
(🦋) /portfolio/po/ $ riskparity

Optimization can take time. Please be patient...

[3 Years] Risk parity portfolio based on risk budgeting approach
using volatility as risk measure

      Weights
┏━━━━━━━┳━━━━━━━━━━┓
┃       ┃ Value    ┃
┡━━━━━━━╇━━━━━━━━━━┩
│ AAPL  │   3.68 % │
├───────┼──────────┤
│ AMZN  │   3.75 % │
├───────┼──────────┤
│ APTV  │   2.46 % │
├───────┼──────────┤
│ ASML  │   2.67 % │
├───────┼──────────┤
│ BABA  │   3.62 % │
├───────┼──────────┤
│ GOOGL │   3.82 % │
├───────┼──────────┤
│ HYG   │   9.53 % │
├───────┼──────────┤
│ IYR   │   4.38 % │
├───────┼──────────┤
│ NKE   │   3.72 % │
├───────┼──────────┤
│ PEX   │   4.27 % │
├───────┼──────────┤
│ PSP   │   3.68 % │
├───────┼──────────┤
│ REZ   │   4.60 % │
├───────┼──────────┤
│ TIP   │  25.52 % │
├───────┼──────────┤
│ TLT   │  20.60 % │
├───────┼──────────┤
│ TSM   │   3.72 % │
└───────┴──────────┘

Annual (by 252) expected return: 4.35%
Annual (by √252) volatility: 14.59%
Sharpe ratio: 0.0317
```

To understand how this portfolio differs from the original portfolio, the <a href="/terminal/reference/portfolio/po/show" target="_blank" rel="noreferrer noopener">show</a> command can be used. This also shows the allocations to each asset class, sector, industry and currency. Using the optimized portfolio, this generates the following results:

```
(🦋) /portfolio/po/ $ show RP_0

Portfolio - RP_0

                            Category - Asset_Class
┏━━━━━┳━━━━━━━━━━━━━━━━┳━━━━━━━━━━━━━━━━━━━━━━━━━┳━━━━━━━━━━━━━━━━━┳━━━━━━━━━━┓
┃     ┃ Asset_Class    ┃ Current_Invested_Amount ┃ Current_Weights ┃ Value    ┃
┡━━━━━╇━━━━━━━━━━━━━━━━╇━━━━━━━━━━━━━━━━━━━━━━━━━╇━━━━━━━━━━━━━━━━━╇━━━━━━━━━━┩
│ USD │ FIXED INCOME   │             2,550,000 $ │         30.03 % │  55.65 % │
├─────┼────────────────┼─────────────────────────┼─────────────────┼──────────┤
│ USD │ PRIVATE EQUITY │               850,000 $ │         10.01 % │   7.95 % │
├─────┼────────────────┼─────────────────────────┼─────────────────┼──────────┤
│ USD │ PUBLIC EQUITY  │             4,242,000 $ │         49.95 % │  27.42 % │
├─────┼────────────────┼─────────────────────────┼─────────────────┼──────────┤
│ USD │ REAL ESTATE    │               850,000 $ │         10.01 % │   8.98 % │
├─────┼────────────────┼─────────────────────────┼─────────────────┼──────────┤
│ USD │ TOTAL USD      │             8,492,000 $ │        100.00 % │ 100.00 % │
└─────┴────────────────┴─────────────────────────┴─────────────────┴──────────┘

                                   Category - Sector
┏━━━━━┳━━━━━━━━━━━━━━━━━━━━━━━━┳━━━━━━━━━━━━━━━━━━━━━━━━━┳━━━━━━━━━━━━━━━━━┳━━━━━━━━━━┓
┃     ┃ Sector                 ┃ Current_Invested_Amount ┃ Current_Weights ┃ Value    ┃
┡━━━━━╇━━━━━━━━━━━━━━━━━━━━━━━━╇━━━━━━━━━━━━━━━━━━━━━━━━━╇━━━━━━━━━━━━━━━━━╇━━━━━━━━━━┩
│ USD │ COMMUNICATION SERVICES │               636,000 $ │          7.49 % │   3.82 % │
├─────┼────────────────────────┼─────────────────────────┼─────────────────┼──────────┤
│ USD │ CONSUMER CYCLICAL      │               751,000 $ │          8.84 % │   7.34 % │
├─────┼────────────────────────┼─────────────────────────┼─────────────────┼──────────┤
│ USD │ CONSUMER DISCRETIONARY │             1,175,000 $ │         13.84 % │   6.21 % │
├─────┼────────────────────────┼─────────────────────────┼─────────────────┼──────────┤
│ USD │ CORPORATE BOND         │               810,000 $ │          9.54 % │   9.53 % │
├─────┼────────────────────────┼─────────────────────────┼─────────────────┼──────────┤
│ USD │ FINANCIALS             │               850,000 $ │         10.01 % │   7.95 % │
├─────┼────────────────────────┼─────────────────────────┼─────────────────┼──────────┤
│ USD │ GOVERNMENT BOND        │             1,740,000 $ │         20.49 % │  46.12 % │
├─────┼────────────────────────┼─────────────────────────┼─────────────────┼──────────┤
│ USD │ INFORMATION TECHNOLOGY │             1,680,000 $ │         19.78 % │  10.06 % │
├─────┼────────────────────────┼─────────────────────────┼─────────────────┼──────────┤
│ USD │ REAL ESTATE            │               850,000 $ │         10.01 % │   8.98 % │
├─────┼────────────────────────┼─────────────────────────┼─────────────────┼──────────┤
│ USD │ TOTAL USD              │             8,492,000 $ │        100.00 % │ 100.00 % │
└─────┴────────────────────────┴─────────────────────────┴─────────────────┴──────────┘

                                            Category - Industry
┏━━━━━┳━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┳━━━━━━━━━━━━━━━━━━━━━━━━━┳━━━━━━━━━━━━━━━━━┳━━━━━━━━━━┓
┃     ┃ Industry                                   ┃ Current_Invested_Amount ┃ Current_Weights ┃ Value    ┃
┡━━━━━╇━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━╇━━━━━━━━━━━━━━━━━━━━━━━━━╇━━━━━━━━━━━━━━━━━╇━━━━━━━━━━┩
│ USD │ AUTO PARTS & EQUIPMENT                     │               429,000 $ │          5.05 % │   2.46 % │
├─────┼────────────────────────────────────────────┼─────────────────────────┼─────────────────┼──────────┤
│ USD │ FINANCIAL SERVICES                         │               850,000 $ │         10.01 % │   7.95 % │
├─────┼────────────────────────────────────────────┼─────────────────────────┼─────────────────┼──────────┤
│ USD │ FOOTWEAR & ACCESSORIES                     │               505,000 $ │          5.95 % │   3.72 % │
├─────┼────────────────────────────────────────────┼─────────────────────────┼─────────────────┼──────────┤
│ USD │ HIGH YIELD BOND                            │               810,000 $ │          9.54 % │   9.53 % │
├─────┼────────────────────────────────────────────┼─────────────────────────┼─────────────────┼──────────┤
│ USD │ INFLATION-PROTECTED BOND                   │               890,000 $ │         10.48 % │  25.52 % │
├─────┼────────────────────────────────────────────┼─────────────────────────┼─────────────────┼──────────┤
│ USD │ INTERACTIVE MEDIA & SERVICES               │               636,000 $ │          7.49 % │   3.82 % │
├─────┼────────────────────────────────────────────┼─────────────────────────┼─────────────────┼──────────┤
│ USD │ INTERNET & DIRECT MARKETING RETAIL         │               992,000 $ │         11.68 % │   7.37 % │
├─────┼────────────────────────────────────────────┼─────────────────────────┼─────────────────┼──────────┤
│ USD │ LONG GOVERNMENT                            │               850,000 $ │         10.01 % │  20.60 % │
├─────┼────────────────────────────────────────────┼─────────────────────────┼─────────────────┼──────────┤
│ USD │ RESIDENTIAL                                │               280,000 $ │          3.30 % │   4.60 % │
├─────┼────────────────────────────────────────────┼─────────────────────────┼─────────────────┼──────────┤
│ USD │ SEMICONDUCTORS                             │             1,300,000 $ │         15.31 % │   6.39 % │
├─────┼────────────────────────────────────────────┼─────────────────────────┼─────────────────┼──────────┤
│ USD │ TECHNOLOGY HARDWARE, STORAGE & PERIPHERALS │               380,000 $ │          4.47 % │   3.68 % │
├─────┼────────────────────────────────────────────┼─────────────────────────┼─────────────────┼──────────┤
│ USD │ TOTAL MARKET                               │               570,000 $ │          6.71 % │   4.38 % │
├─────┼────────────────────────────────────────────┼─────────────────────────┼─────────────────┼──────────┤
│ USD │ TOTAL USD                                  │             8,492,000 $ │        100.00 % │ 100.00 % │
└─────┴────────────────────────────────────────────┴─────────────────────────┴─────────────────┴──────────┘

                              Category - Country
┏━━━━━┳━━━━━━━━━━━━━━━┳━━━━━━━━━━━━━━━━━━━━━━━━━┳━━━━━━━━━━━━━━━━━┳━━━━━━━━━━┓
┃     ┃ Country       ┃ Current_Invested_Amount ┃ Current_Weights ┃ Value    ┃
┡━━━━━╇━━━━━━━━━━━━━━━╇━━━━━━━━━━━━━━━━━━━━━━━━━╇━━━━━━━━━━━━━━━━━╇━━━━━━━━━━┩
│ USD │ ASIA          │               626,000 $ │          7.37 % │   7.34 % │
├─────┼───────────────┼─────────────────────────┼─────────────────┼──────────┤
│ USD │ EUROPE        │             1,425,000 $ │         16.78 % │   6.39 % │
├─────┼───────────────┼─────────────────────────┼─────────────────┼──────────┤
│ USD │ UNITED STATES │             6,441,000 $ │         75.85 % │  86.28 % │
├─────┼───────────────┼─────────────────────────┼─────────────────┼──────────┤
│ USD │ TOTAL USD     │             8,492,000 $ │        100.00 % │ 100.00 % │
└─────┴───────────────┴─────────────────────────┴─────────────────┴──────────┘
```

It is possible to use the commands without loading in the parameters template or by using the parameters template but changing some arguments directly into the terminal. For example, using the same method as described above, the risk measure is changed to <a href="https://www.investopedia.com/terms/c/conditional_value_at_risk.asp" target="_blank" rel="noreferrer noopener">Conditional Value at Risk (CVaR)</a> and the used historic period is increased to 5 years (keeping all other parameters unchanged):

```
(🦋) /portfolio/po/ $ riskparity -rm CVaR -p 5y

Optimization can take time. Please be patient...

[5 Years] Risk parity portfolio based on risk budgeting approach
using conditional value at risk (CVaR) as risk measure

      Weights
┏━━━━━━━┳━━━━━━━━━━┓
┃       ┃ Value    ┃
┡━━━━━━━╇━━━━━━━━━━┩
│ AAPL  │   3.73 % │
├───────┼──────────┤
│ AMZN  │   3.27 % │
├───────┼──────────┤
│ APTV  │   2.68 % │
├───────┼──────────┤
│ ASML  │   2.75 % │
├───────┼──────────┤
│ BABA  │   4.10 % │
├───────┼──────────┤
│ GOOGL │   3.59 % │
├───────┼──────────┤
│ HYG   │   9.43 % │
├───────┼──────────┤
│ IYR   │   4.36 % │
├───────┼──────────┤
│ NKE   │   3.42 % │
├───────┼──────────┤
│ PEX   │   4.16 % │
├───────┼──────────┤
│ PSP   │   3.60 % │
├───────┼──────────┤
│ REZ   │   4.58 % │
├───────┼──────────┤
│ TIP   │  26.33 % │
├───────┼──────────┤
│ TLT   │  20.29 % │
├───────┼──────────┤
│ TSM   │   3.70 % │
└───────┴──────────┘

Annual (by 252) expected return: 6.99%
Annual (by √252) volatility: 12.21%
Sharpe ratio: 0.2538
Annual (by √252) conditional value at risk (CVaR) : 28.63%
Return / conditional value at risk (CVaR) ratio: 0.1083
```

## Examples

The example portfolio is again loaded in:

```
(🦋) /portfolio/po/ $ load --example

Loading an example, please type `about` to learn how to create your own Portfolio Optimization Excel sheet.


(🦋) /portfolio/po/ $ ?

╭────────────────────────────────────────────────────────────────────────── Portfolio - Portfolio Optimization ───────────────────────────────────────────────────────────────────────────╮
│                                                                                                                                                                                         │
│     load               load tickers and categories from .xlsx or .csv file                                                                                                              │
│                                                                                                                                                                                         │
│ Portfolio loaded: OpenBB Example Portfolio                                                                                                                                              │
│                                                                                                                                                                                         │
│ Tickers: AAPL, AMZN, APTV, ASML, BABA, GOOGL, HYG, IYR, NKE, PEX, PSP, REZ, TIP, TLT, TSM                                                                                               │
│ Categories: ASSET_CLASS, SECTOR, INDUSTRY, COUNTRY, CURRENCY                                                                                                                            |
<continues>
```

It is possible to load the parameters template here but this is not necessary as each parameter has a default value set regardless. However, because the Excel file provides a more structured way of presenting the choices, the template is loaded in:

```
(🦋) /portfolio/po/ $ file --file parameters_template.xlsx
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

Then, the <a href="https://jpm.pm-research.com/content/42/4/59.short" target="_blank" rel="noreferrer noopener">Hierarchical Risk Parity</a> technique is applied by running the <a href="/terminal/reference/portfolio/po/hrp/" target="_blank" rel="noreferrer noopener">hrp</a> command. This results in the following:

```
(🦋) /portfolio/po/ $ hrp

Optimization can take time. Please be patient...

[3 Years] Hierarchical risk parity portfolio using pearson codependence,
single linkage and volatility as risk measure

      Weights
┏━━━━━━━┳━━━━━━━━━━┓
┃       ┃ Value    ┃
┡━━━━━━━╇━━━━━━━━━━┩
│ AAPL  │   1.47 % │
├───────┼──────────┤
│ AMZN  │   2.54 % │
├───────┼──────────┤
│ APTV  │   0.44 % │
├───────┼──────────┤
│ ASML  │   0.93 % │
├───────┼──────────┤
│ BABA  │   0.64 % │
├───────┼──────────┤
│ GOOGL │   1.68 % │
├───────┼──────────┤
│ HYG   │  10.46 % │
├───────┼──────────┤
│ IYR   │   1.28 % │
├───────┼──────────┤
│ NKE   │   1.33 % │
├───────┼──────────┤
│ PEX   │   1.31 % │
├───────┼──────────┤
│ PSP   │   1.75 % │
├───────┼──────────┤
│ REZ   │   1.39 % │
├───────┼──────────┤
│ TIP   │  62.12 % │
├───────┼──────────┤
│ TLT   │  11.40 % │
├───────┼──────────┤
│ TSM   │   1.26 % │
└───────┴──────────┘

Annual (by 252) expected return: 2.48%
Annual (by √252) volatility: 9.13%
Sharpe ratio: -0.1546
```

This optimization process is then compared with the current holdings. To keep things manageable, only the sector allocations are compared between the unoptimized and optimized portfolio which is done with the <a href="/terminal/reference/portfolio/po/show/" target="_blank" rel="noreferrer noopener">show</a> command:

```
(🦋) /portfolio/po/ $ show _HRP0 -ct SECTOR

Current Portfolios: _HRP0

Current Categories: INDUSTRY, CURRENT_INVESTED_AMOUNT, ASSET_CLASS, COUNTRY, CURRENCY, SECTOR

Portfolio: _HRP0

                                   Category - Sector
┏━━━━━┳━━━━━━━━━━━━━━━━━━━━━━━━┳━━━━━━━━━━━━━━━━━━━━━━━━━┳━━━━━━━━━━━━━━━━━┳━━━━━━━━━━┓
┃     ┃ Sector                 ┃ Current_Invested_Amount ┃ Current_Weights ┃ Value    ┃
┡━━━━━╇━━━━━━━━━━━━━━━━━━━━━━━━╇━━━━━━━━━━━━━━━━━━━━━━━━━╇━━━━━━━━━━━━━━━━━╇━━━━━━━━━━┩
│ USD │ COMMUNICATION SERVICES │               636,000 $ │          7.49 % │   1.68 % │
├─────┼────────────────────────┼─────────────────────────┼─────────────────┼──────────┤
│ USD │ CONSUMER CYCLICAL      │               751,000 $ │          8.84 % │   1.97 % │
├─────┼────────────────────────┼─────────────────────────┼─────────────────┼──────────┤
│ USD │ CONSUMER DISCRETIONARY │             1,175,000 $ │         13.84 % │   2.98 % │
├─────┼────────────────────────┼─────────────────────────┼─────────────────┼──────────┤
│ USD │ CORPORATE BOND         │               810,000 $ │          9.54 % │  10.46 % │
├─────┼────────────────────────┼─────────────────────────┼─────────────────┼──────────┤
│ USD │ FINANCIALS             │               850,000 $ │         10.01 % │   3.06 % │
├─────┼────────────────────────┼─────────────────────────┼─────────────────┼──────────┤
│ USD │ GOVERNMENT BOND        │             1,740,000 $ │         20.49 % │  73.52 % │
├─────┼────────────────────────┼─────────────────────────┼─────────────────┼──────────┤
│ USD │ INFORMATION TECHNOLOGY │             1,680,000 $ │         19.78 % │   3.66 % │
├─────┼────────────────────────┼─────────────────────────┼─────────────────┼──────────┤
│ USD │ REAL ESTATE            │               850,000 $ │         10.01 % │   2.67 % │
├─────┼────────────────────────┼─────────────────────────┼─────────────────┼──────────┤
│ USD │ TOTAL USD              │             8,492,000 $ │        100.00 % │ 100.00 % │
└─────┴────────────────────────┴─────────────────────────┴─────────────────┴──────────┘
```

This table shows how the portfolio changed and how much is allocated to each sector. It is possible to delve further into these findings with the <a href="/terminal/reference/portfolio/po/plot/" target="_blank" rel="noreferrer noopener">plot</a> command. This gives the ability to visually depict allocations, e.g. below the sector allocation is visually depicted.

```
(🦋) /portfolio/po/ $ plot --portfolios _HRP0 -ct SECTOR -pi
```

![Sectors Pie Chart](https://user-images.githubusercontent.com/46355364/213746043-58cd5d69-6e62-4ebd-b12c-724be62458ac.png)

Further analysis can be done by looking at the portfolio's returns <a href="https://www.investopedia.com/terms/h/histogram.asp" target="_blank" rel="noreferrer noopener">histogram</a> which also includes a variety of risk measures as well as the portfolio's drawdowns.

````
(🦋) /portfolio/po/ $ plot --portfolios _HRP0 -ct SECTOR -hi -dd
````

![Portfolio Returns Histogram](https://user-images.githubusercontent.com/46355364/213745938-f6f97e06-287c-4c0d-a4f1-bc23828b346e.png)
![Portfolio Drawdowns](https://user-images.githubusercontent.com/46355364/213746000-5f7f6bc0-9f5c-4be3-a217-12551c79bcee.png)

Next to that, to delve deeper in the underlying conclusions the HRP method has drawn. Here, a closer look can be given to the assets cluster map, which links certain categories to each other. The linkage process is done per asset basis but here it is grouped per sector. Based on these results, the user can identify whether the optimization techniques also logically makes sense.

````
(🦋) /portfolio/po/ $ plot --portfolios _HRP0 -ct SECTOR -rc -he
````
![Heatmap with Linkage Method](https://user-images.githubusercontent.com/46355364/213745877-8d0ab932-7775-4c9b-be60-da614c338b8d.png)
![Risk Contributions](https://user-images.githubusercontent.com/46355364/213745808-d4dede01-a16c-4b3f-83a7-f8b2096896e3.png)
