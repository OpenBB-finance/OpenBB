```
usage: infer [-l LIMIT] [-h] [--export {csv,json,xlsx}]
```

Displays a quick sentiment inference from last tweets that contain the ticker. This model splits the text into character-level tokens and uses vader
sentiment analysis. Source: <https://Twitter.com>

```
optional arguments:
  -l LIMIT, --limit LIMIT
                        limit of latest tweets to infer from. (default: 100)
  -h, --help            show this help message (default: False)
  --export {csv,json,xlsx,png,jpg,pdf,svg}
                        Export raw data into csv, json, xlsx (default: )
```

Example:

```
2022 Feb 19, 13:05 (🦋) /stocks/ba/ $ infer
From: 2022-02-19 17:08:20
To:   2022-02-19 18:04:18
100 tweets were analyzed.
Frequency of approx 1 tweet every 34 seconds.
The summed compound sentiment of AAPL is: 13.2
The average compound sentiment of AAPL is: 0.13
Of the last 100 tweets, 45.00 % had a higher positive sentiment
Of the last 100 tweets, 18.00 % had a higher negative sentiment
```
