```
usage: whatif [-d DATE_SHARES_ACQUIRED] [-n NUM_SHARES_ACQUIRED] [-h]
```

Displays what if scenario of having bought X shares at date Y

```
optional arguments:
  -d DATE_SHARES_ACQUIRED, --date DATE_SHARES_ACQUIRED
                        Date at which the shares were acquired (default: None)
  -n NUM_SHARES_ACQUIRED, --number NUM_SHARES_ACQUIRED
                        Number of shares acquired (default: 1.0)
  -h, --help            show this help message (default: False)
```

```

(✨) /stocks/bt/ $ whatif -n 2
IPO date selected by default.
If you had acquired 2 shares of TSLA on 2010-06-29 with a cost of 9.56.
These would be worth 2129.58. Which represents an increase of 22285.28%. 

(✨) /stocks/bt/ $ whatif 2021-01-01
If you had acquired 1 share of TSLA on 2021-01-01 with a cost of 729.77.
This would be worth 1065.45. Which represents an increase of 146.00%. 

(✨) /stocks/bt/ $ whatif
IPO date selected by default.
If you had acquired 1 share of TSLA on 2010-06-29 with a cost of 4.78.
This would be worth 1065.28. Which represents an increase of 22295.52%. 
```
