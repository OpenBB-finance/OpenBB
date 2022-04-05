# Portfolio Optimization [>>](https://gamestonkterminal.github.io/GamestonkTerminal/portfolio/portfolio_optimization/)

Command|Description
------ | ------------
`select`        |select list of tickers to be optimized
`add`           |add tickers to the list of the tickers to be optimized
`rmv`           |remove tickers from the list of the tickers to be optimized
|
`maxsharpe`     |maximal Sharpe ratio portfolio (a.k.a the tangency portfolio)
`minrisk`       |minimum risk portfolio
`maxutil`       |maximal risk averse utility function, given some risk aversion parameter
`maxret`        |maximal return portfolio
`ef`            |show the efficient frontier
|
`riskparity`    |risk parity portfolio using risk budgeting approach
`relriskparity` |relaxed risk parity using least squares approach
|
`hrp`           |hierarchical risk parity
`herc`          |hierarchical equal risk contribution
`nco`	        |nested clustering optimization
|
`equal`         |equally weighted
`mktcap`        |weighted according to market cap (property marketCap)
`dividend`      |weighted according to dividend yield (property dividendYield)
`property`      |weight according to selected info property
`maxdiv`        |maximum diversification portfolio
`maxdecorr`     |maximum decorrelation portfolio
|
