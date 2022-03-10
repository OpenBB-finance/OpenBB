```
usage: build [-s START] [-t TICKERS] [-c CLASSES] [-w WEIGHTS] [-a AMOUNT] [-h]
```

Build portfolio from list of tickers and weights

```
optional arguments:
  -s START, --start START
                        Start date. (default: 2021-01-04)
  -t TICKERS, --tickers TICKERS
                        List of symbols separated by commas (i.e AAPL,BTC,DOGE,SPY....) (default: None)
  -c CLASSES, --class CLASSES
                        Asset class (stock, crypto, etf), separated by commas. (default: None)
  -w WEIGHTS, --weights WEIGHTS
                        List of weights, separated by comma (default: None)
  -a AMOUNT, --amount AMOUNT
                        Amount to allocate initially. (default: 100000)
  -h, --help            show this help message (default: False)

```

The method of listing trades has resulted in some confusion, so this method is meant to just  give portfolio statistics
for a custom assortment of tickers and weights.  The drawback is that this assumes everything is bought on the same day
at 'the closing price'.  

An example of a build is below.  This assumes that $100,000 dollars was invested on Jan 5 2018,
50% allocated to AAPL, and then 25% to bitcoin and 25% to NFLX.

```
build -t aapl,btc,nflx -c stock,crypto,stock -w .5,.25,.25 -s 2018-01-05 -a 100_000
```
Currently the weights should add to 1 (so technically shorting is allowed as long as you have a net weights of 1).
