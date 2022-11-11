```
usage: news [-l LIMIT] [-k {news,media}]
            [--filter {rising,hot,bullish,bearish,important,saved,lol}]
            [-r {en,de,es,fr,nl,it,pt,ru}]
            [-s {published_at,domain,title,negative_votes,positive_votes}] [--reverse]
            [-u] [-h] [--export EXPORT]
```

Display most recent news on the given coin from CryptoPanic aggregator platform. [Source: https://cryptopanic.com/]

```
optional arguments:
  -l LIMIT, --limit LIMIT
                        display N number records (default: 10)
  -k {news,media}, --kind {news,media}
                        Filter by category of news. Available values: news or media.
                        (default: news)
  --filter {rising,hot,bullish,bearish,important,saved,lol}
                        Filter by kind of news. One from list:
                        rising|hot|bullish|bearish|important|saved|lol (default: None)
  -r {en,de,es,fr,nl,it,pt,ru}, --region {en,de,es,fr,nl,it,pt,ru}
                        Filter news by regions. Available regions are: en (English), de
                        (Deutsch), nl (Dutch), es (Español), fr (Français), it (Italiano),
                        pt (Português), ru (Русский) (default: en)
  -s {published_at,domain,title,negative_votes,positive_votes}, --sort {published_at,domain,title,negative_votes,positive_votes}
                        Sort by given column. Default: published_at (default:
                        published_at)
  --reverse             Data is sorted in descending order by default.
                        Reverse flag will sort it in an ascending way.
                        Only works when raw data is displayed. (default: False)
  -u, --urls            Flag to disable urls. If you will use the flag you will hide the
                        column with urls (default: True)
  -h, --help            show this help message (default: False)
  --export EXPORT       Export raw data into csv, json, xlsx (default: )
```

Example:

```
2022 Apr 25, 09:49 (🦋) /crypto/dd/ $ news
                                             Most Recent News
┏━━━━━━━━━━━━━━┳━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┳━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
┃ published_at ┃ title                                       ┃ link                                       ┃
┡━━━━━━━━━━━━━━╇━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━╇━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┩
│ 2022-04-24   │ Major German Bank Applies For Crypto        │ https://cryptopanic.com/news/15005355/Maj… │
│              │ Custody License                             │                                            │
├──────────────┼─────────────────────────────────────────────┼────────────────────────────────────────────┤
│ 2022-04-24   │ These Two Companies Will Let You Buy a      │ https://cryptopanic.com/news/15005488/The… │
│              │ House with Crypto                           │                                            │
├──────────────┼─────────────────────────────────────────────┼────────────────────────────────────────────
```
