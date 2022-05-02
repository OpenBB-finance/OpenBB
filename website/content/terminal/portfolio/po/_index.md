---
geekdocCollapseSection: true
---

The terminal has incorporated Riskfolio-Lib. Refer to the documentation here: <http://riskfolio-lib.readthedocs.io/>

```text
Parameter file:

    file          select portfolio parameter file
>   params        specify and show portfolio risk parameters
    load          load tickers and categories from .xlsx or .csv file

Portfolio Optimization:
    add           add tickers to the list of the tickers to be optimized
    rmv           remove tickers from the list of the tickers to be optimized
    show          show selected portfolios and categories from the list of saved portfolios
    rpf           remove portfolios from the list of saved portfolios
    plot          plot selected charts from the list of saved portfolios

Tickers: BLL, CLX, CSCO, DE, HD, IBM, MAS, MTB, OKE, PCG, RCL, SCHW, SYY, VZ, XRAY
Categories: ASSET_CLASS, SECTOR, INDUSTRY, COUNTRY, CURRENT_INVESTED_AMOUNT, CURRENCY
Portfolios: MINRISK_0, MAXSHARPE_1

Mean Risk Optimization:
    maxsharpe       maximal Sharpe ratio portfolio (a.k.a the tangency portfolio)
    minrisk         minimum risk portfolio
    maxutil         maximal risk averse utility function, given some risk
                    aversion parameter
    maxret          maximal return portfolio
    maxdiv          maximum diversification portfolio
    maxdecorr       maximum decorrelation portfolio
    blacklitterman  black litterman portfolio
    ef              show the efficient frontier

Risk Parity Optimization:
    riskparity    risk parity portfolio using risk budgeting approach
    relriskparity relaxed risk parity using least squares approach

Hierarchical Clustering Models:
    hrp           hierarchical risk parity
    herc          hierarchical equal risk contribution
    nco           nested clustering optimization

Other Optimization Techniques:
    equal         equally weighted
    mktcap        weighted according to market cap (property marketCap)
    dividend      weighted according to dividend yield (property dividendYield)
    property      weight according to selected info property
```

{{< toc-tree >}}