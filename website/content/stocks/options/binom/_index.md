```
usage: binom [-s STRIKE] [-p] [-e] [-E] [-P] [-v VOLATILITY] [-h]
```

Shows the value of an option using binomial option pricing. Can also show raw data and provide a graph with predicted underlying asset ending values. The binomial options model calculates how big an up step or down step in the next time period will likely be. Then it creates a tree doing this at each period. The end results of this is a tree with possible asset values at each "step". For our calculations we use a day as our "step" time period. We then take all of the expected values at the finishing date and use this to begin a tree of option values at each step. The ending results is the value of the option today.

```
optional arguments:
  -s STRIKE, --strike STRIKE
                        strike price for the option (default: 0)
  -p, --put             value the option as a put (default: False)
  -e, --european        value the option as a European option (default: False)
  --export              export the binomial trees (default: False)
  -P, --plot            plots the expected underlying asset ending prices (default: False)
  -v, --volatility      sets the volatility for the underlying asset(default: None)
  -h, --help            show this help message (default: False)
```
