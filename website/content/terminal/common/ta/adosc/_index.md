```txt
usage: adosc [--open] [--fast N_LENGTH_FAST] [--slow N_LENGTH_SLOW] [--export {csv,json,xlsx}] [-h]
```

Acummulation/Distribution Oscillator, also known as the Chaikin Oscillator is essentially a momentum indicator, but of the Accumulation-Distribution line rather than merely price. It looks at both the strength of price moves and the underlying buying and selling pressure during a given time period. The oscillator reading above zero indicates net buying pressure, while one below zero registers net selling pressure. Divergence between the indicator and pure price moves are the most common signals from the indicator, and often flag market turning points.

```txt
optional arguments:
  --open                uses open value of stock (default: False)
  --fast N_LENGTH_FAST
                        fast length (default: 3)
  --slow N_LENGTH_SLOW
                        slow length (default: 10)
  --export {csv,json,xlsx}
                        Export dataframe data to csv,json,xlsx file (default: )
  -h, --help            show this help message (default: False)
```

![adosc](https://user-images.githubusercontent.com/46355364/154309482-31c027ab-e80f-4145-9c63-392a74cf69c7.png)
