```
usage: sentiment [-l LIMIT] [-d N_DAYS_PAST] [-h] [--export {csv,json,xlsx,png,jpg,pdf,svg}]
```

Plot in-depth sentiment predicted from tweets from last days that contain pre-defined ticker. [Source: Twitter]

```
optional arguments:
  -l LIMIT, --limit LIMIT
                        limit of tweets to extract per hour. (default: 15)
  -d N_DAYS_PAST, --days N_DAYS_PAST
                        number of days in the past to extract tweets. (default: 6)
  -h, --help            show this help message (default: False)
  --export {csv,json,xlsx,png,jpg,pdf,svg}
                        Export raw data into csv, json, xlsx and figure into png, jpg, pdf, svg (default: )
```
Example:
```
2022 Feb 19, 13:16 (✨) /stocks/ba/ $ sentiment
From 2022-02-19 retrieving 360 tweets (15 tweets/hour)
From 2022-02-18 retrieving 360 tweets (15 tweets/hour)
From 2022-02-17 retrieving 360 tweets (15 tweets/hour)
From 2022-02-16 retrieving 360 tweets (15 tweets/hour)
From 2022-02-15 retrieving 360 tweets (15 tweets/hour)
From 2022-02-14 retrieving 360 tweets (15 tweets/hour)
From 2022-02-13 retrieving 360 tweets (15 tweets/hour)
```

<img size="1400" alt="Feature Screenshot - sentiment" src="https://user-images.githubusercontent.com/18151143/154813738-58dc44c8-19b5-4c2e-912c-e74e239b93e8.png">
