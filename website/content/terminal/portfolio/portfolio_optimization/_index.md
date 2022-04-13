---
geekdocCollapseSection: true
---

The terminal has incorporated Riskfolio-Lib. Refer to the documentation here: <http://riskfolio-lib.readthedocs.io/>

```text
Portfolio Optimization:
    select        select list of tickers to be optimized
    add           add tickers to the list of the tickers to be optimized
    rmv           remove tickers from the list of the tickers to be optimized
    show          show selected portfolios from the list of saved portfolios
    rpf           remove portfolios from the list of saved portfolios

Tickers: VT, QQQ, SPY
Portfolios: MINRISK_0, MAXSHARPE_1

Mean Risk Optimization:
    maxsharpe     maximal Sharpe ratio portfolio (a.k.a the tangency portfolio)
    minrisk       minimum risk portfolio
    maxutil       maximal risk averse utility function, given some risk
                  aversion parameter
    maxret        maximal return portfolio
    ef            show the efficient frontier

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
    maxdiv        maximum diversification portfolio
    maxdecorr     maximum decorrelation portfolio[
```

{{< toc-tree >}}
