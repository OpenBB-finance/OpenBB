```
usage: news [-n N_NUM] [-d N_START_DATE] [-o] [-s N_SOURCES [N_SOURCES ...]] [-h]
```
Using the [loaded ticker](https://gamestonkterminal.github.io/GamestonkTerminal/stocks/load/), the 'news' command will search articles and blogs with the [News API](https://newsapi.org) where the ticker symbol or company name are mentioned. Searches are limited to the past thirty days when using the free API key available. Searches may bring unwanted results when the ticker or business name contains words used as the Dictionary defines.  Optional arguments can be added to the command string as described below. 

```
optional arguments:
  -n N_NUM, --num N_NUM
                        Number of latest news being printed.
  -d N_START_DATE, --date N_START_DATE
                        The starting date (format YYYY-MM-DD) to search articles from
  -o, --oldest          Show oldest articles first
  -s N_SOURCES [N_SOURCES ...], --sources N_SOURCES [N_SOURCES ...]
                        Show news only from the sources specified (e.g bbc yahoo.com)
  -h, --help            show this help message
```
<img width="1399" alt="Feature Screenshot - News" src="https://user-images.githubusercontent.com/85772166/140126730-3e148862-e1b3-4a27-b322-3b6fd432c7a5.png">
