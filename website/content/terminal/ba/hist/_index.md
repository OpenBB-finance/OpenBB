```
usage: hist [-s START] [-e END] [-n NUMBER] [-h] [--export {csv,json,xlsx,png,jpg,pdf,svg}] [--raw] [-l LIMIT]
```

Plot historical sentiment data of RHI and AHI by hour. Source: [Sentiment Investor]

AHI (Absolute Hype Index)
---

AHI is a measure of how much people are talking about a stock on social media.
It is calculated by dividing the total number of mentions for the chosen stock on a social network by the mean number of mentions any stock receives on that social medium.

RHI (Relative Hype Index)
---

RHI is a measure of whether people are talking about a stock more or less than usual, calculated by dividing the mean AHI for the past day by the mean AHI for for the past week for that stock.

```
optional arguments:
  -s START, --start START
                        The starting date (format YYYY-MM-DD) of the stock. Default: 7 days ago (default: 2022-02-09)
  -e END, --end END     The ending date (format YYYY-MM-DD) of the stock. Default: today (default: 2022-02-16)
  -n NUMBER, --number NUMBER
                        Number of results returned from Sentiment Investor. Default: 100 (default: 100)
  -h, --help            show this help message (default: False)
  --export {csv,json,xlsx,png,jpg,pdf,svg}
                        Export raw data into csv, json, xlsx and figure into png, jpg, pdf, svg (default: )
  --raw                 Flag to display raw data (default: False)
  -l LIMIT, --limit LIMIT
                        Number of entries to show in data. (default: 10)
```

Example:

```
2022 Feb 16, 10:23 (🦋) /stocks/ba/ $ load TSLA

Loading Daily TSLA stock with starting period 2019-02-11 for analysis.

Datetime: 2022 Feb 16 10:23
Timezone: America/New_York
Currency: USD
Market:   CLOSED

2022 Feb 16, 10:23 (🦋) /stocks/ba/ $ hist
```

![hist](https://user-images.githubusercontent.com/46355364/154296923-af6a4b2d-ab16-44d1-8270-e5926f4bac16.png)
