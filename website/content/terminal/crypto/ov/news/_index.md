```
usage: news [-l N] [-k {news,media}]
            [-f {rising,hot,bullish,bearish,important,saved,lol}]
            [-r {en,de,es,fr,nl,it,pt,ru}]
            [-s {published_at,domain,title,negative_votes,positive_votes}]
            [--descend] [-l] [-h] [--export {png,jpg,pdf,svg}]

```

Display recent posts from CryptoPanic news aggregator platform. [Source:https://cryptopanic.com/]

```
optional arguments:
  -l N, --limit N      N number of news >=10 (default: 20)
  -k {news,media}, --kind {news,media}
                        Filter by category of news. Available values: news or
                        media. (default: news)
  -f {rising,hot,bullish,bearish,important,saved,lol}, --filter {rising,hot,bullish,bearish,important,saved,lol}
                        Filter by kind of news. One from list:
                        rising|hot|bullish|bearish|important|saved|lol
                        (default: None)
  -r {en,de,es,fr,nl,it,pt,ru}, --region {en,de,es,fr,nl,it,pt,ru}
                        Filter news by regions. Available regions are: en
                        (English), de (Deutsch), nl (Dutch), es (Español), fr
                        (Français), it (Italiano), pt (Português), ru
                        (Русский) (default: en)
  -s {published_at,domain,title,negative_votes,positive_votes}, --sort {published_at,domain,title,negative_votes,positive_votes}
                        Sort by given column. Default: published_at (default:
                        published_at)
  --descend             Flag to sort in descending order (lowest first)
                        (default: True)
  -u, --urls           Flag to show urls. If you will use that flag you will
                        additional column with urls (default: False)
  -h, --help            show this help message (default: False)
  --export {png,jpg,pdf,svg}
                        Export or figure into png, jpg, pdf, svg (default: )
```
