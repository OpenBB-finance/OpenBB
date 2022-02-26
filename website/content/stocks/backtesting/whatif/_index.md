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

Example:
```
2022 Feb 16, 10:05 (✨) /stocks/bt/ $ whatif -d 2020-01-01 -n 100
If you had acquired 100 shares of MSFT on 2020-01-01 with a cost of 15761.51.
These would be worth 29462.01. Which represents an increase of 86.92%.

2022 Feb 16, 10:05 (✨) /stocks/bt/ $ whatif -d 2010-01-01 -n 100
If you had acquired 100 shares of MSFT on 2010-01-01 with a cost of 2390.50.
These would be worth 29444.00. Which represents an increase of 1131.71%.

2022 Feb 16, 10:05 (✨) /stocks/bt/ $ whatif -d 2000-01-01 -n 100
If you had acquired 100 shares of MSFT on 2000-01-01 with a cost of 3679.42.
These would be worth 29450.00. Which represents an increase of 700.40%.

2022 Feb 16, 10:05 (✨) /stocks/bt/ $
```
