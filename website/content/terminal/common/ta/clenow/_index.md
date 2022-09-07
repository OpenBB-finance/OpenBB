```
usage: clenow [-p PERIOD] [-h] [--export EXPORT]
```
Calculates the Clenow Volatility Adjusted Momentum.

This indicator is calculated by performing a regression on log prices.  The factor is obtained by multiplying the
regression coefficient with the R2 of the regression.  

An example of the use of this strategy can be found at:
https://www.quant-investing.com/blog/this-easy-to-use-adjusted-slope-momentum-strategy-performed-7-times-better-than-the-market

```
options:
  -p PERIOD, --period PERIOD
                        Lookback period for regression (default: 90)
  -h, --help            show this help message (default: False)
  --export EXPORT       Export figure into png, jpg, pdf, svg (default: )

For more information and examples, use 'about clenow' to access the related guide.
```