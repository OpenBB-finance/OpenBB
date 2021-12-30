```
usage: maxsharpe [-p {1d,5d,1mo,3mo,6mo,1y,2y,5y,10y,ytd,max}] [-v VALUE] [--pie] [-r RISK_FREE_RATE] [-h]
```
The Sharpe ratio is one of the most widely used methods for calculating risk-adjusted return. Modern Portfolio Theory (MPT) states that adding assets to a diversified portfolio that has low correlations can decrease portfolio risk without sacrificing returns. Adding diversification should increase the Sharpe ratio compared to similar portfolios with a lower level of diversification. For this to be true, investors must also accept the assumption that risk is equal to volatility, which is not unreasonable but may be too narrow to be applied to all investments.

The Sharpe Ratio is calculated as follows: 

1. Subtract the risk-free rate from the return of the portfolio. The risk-free rate could be a U.S. Treasury rate or yield, such as the one-year or two-year Treasury yield.

2. Divide the result by the standard deviation of the portfolio’s excess return. The standard deviation helps to show how much the portfolio's return deviates from the expected return. The standard deviation also sheds light on the portfolio's volatility.

The Sharpe ratio can also help explain whether a portfolio's excess returns are due to smart investment decisions or a result of too much risk.

```
optional arguments:
  -p {1d,5d,1mo,3mo,6mo,1y,2y,5y,10y,ytd,max}, --period {1d,5d,1mo,3mo,6mo,1y,2y,5y,10y,ytd,max}
                        period to get yfinance data from (default: 3mo)
  -v VALUE, --value VALUE
                        Amount to allocate to portfolio (default: 1.0)
  --pie                 Display a pie chart for weights (default: False)
  -r RISK_FREE_RATE, --risk-free-rate RISK_FREE_RATE
                        Risk-free rate of borrowing/lending. The period of the risk-free rate should correspond to the frequency of expected returns.
                        (default: 0.02)
  -h, --help            show this help message (default: False)
```
<img width="1400" alt="Feature Screenshot - maxsharpe" src="https://user-images.githubusercontent.com/85772166/147481783-0b8f3ecf-8946-49a9-bd97-3db2a0348b3d.png">
