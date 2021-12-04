```
usage: binom [-s STRIKE] [-p] [-e] [-E] [-P] [-v VOLATILITY] [-h]
```

Shows the value of an option using binomial option pricing. Can also show raw data and provide a graph with predicted underlying asset ending values.

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
<img size="1400" alt="Feature Screenshot - oi" src="https://user-images.githubusercontent.com/85772166/142368338-403b2d8d-00ea-4052-a643-683f5ee79711.png">
