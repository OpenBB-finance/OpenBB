# Portfolio Optimization [>>](https://gamestonkterminal.github.io/GamestonkTerminal/portfolio/portfolio_optimization/)

Command|Description
------ | ------------
`select`        |select list of tickers to be optimized
`add`           |add tickers to the list of the tickers to be optimized
`rmv`           |remove tickers from the list of the tickers to be optimized
|
`equal`         |equally weighted
`mktcap`        |weighted according to market cap (property marketCap)
`dividend`      |weighted according to dividend yield (property dividendYield)
`property`      |weight according to selected info property
|
`maxsharpe`     |optimizes for maximal Sharpe ratio (a.k.a the tangency portfolio
`minvol`        |optimizes for minimum volatility
`maxquadutil`   |maximises the quadratic utility, given some risk aversion
`effret`        |maximises return for a given target risk
`effrisk`       |minimises risk for a given target return
|
`ef`            |show the efficient frontier
