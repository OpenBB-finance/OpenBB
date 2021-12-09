```
usage: adosc [--open] [-f N_LENGTH_FAST] [-s N_LENGTH_SLOW] [--export {csv,json,xlsx}] [-h]
```

Acummulation/Distribution Oscillator, also known as the Chaikin Oscillator is essentially a momentum indicator, but of the Accumulation-Distribution line rather than merely price. It looks at both the strength of price moves and the underlying buying and selling pressure during a given time period. The oscillator reading above zero indicates net buying pressure, while one below zero registers net selling pressure. Divergence between the indicator and pure price moves are the most common signals from the indicator, and often flag market turning points.

```
optional arguments:
  --open                uses open value of stock (default: False)
  -f N_LENGTH_FAST, --fast_length N_LENGTH_FAST
                        fast length (default: 3)
  -s N_LENGTH_SLOW, --slow_length N_LENGTH_SLOW
                        slow length (default: 10)
  --export {csv,json,xlsx}
                        Export dataframe data to csv,json,xlsx file (default: )
  -h, --help            show this help message (default: False)
```
<img size="1400" alt="Feature Screenshot - adosc" src="https://user-images.githubusercontent.com/85772166/143980871-6e658d3e-39a7-4192-8477-4e0e79dd8ca5.png">
