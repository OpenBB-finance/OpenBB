```
usage: news [-n N_NUM] [-d N_START_DATE] [-o] [-s SOURCES [SOURCES ...]] [-h]
```

Using the loaded ticker, the 'news' command will search articles and blogs with the [News API](https://newsapi.org) where the ticker symbol or company name are mentioned. Searches are limited to the past thirty days when using the free API key available. Searches may bring unwanted results when the ticker or business name contains words used as the Dictionary defines. Optional arguments can be added to the command string as described below.

```
optional arguments:
  -n N_NUM, --num N_NUM
                        Number of latest news being printed.
  -d N_START_DATE, --date N_START_DATE
                        The starting date (format YYYY-MM-DD) to search articles from
  -o, --oldest          Show oldest articles first
  -s SOURCES [SOURCES ...], --sources SOURCES [SOURCES ...]
                        Show news only from the sources specified (e.g bbc yahoo.com)
  -h, --help            show this help message
```

Example:
```
2022 Feb 16, 08:33 (✨) /stocks/ $ news
256 news articles for Amazon.com,+Inc. were found since 2022-02-09

2022-02-16 13:06:33   ViacomCBS renames itself Paramount
https://www.livemint.com/industry/media/viacomcbs-renames-itself-paramount-11645016266083.html

2022-02-16 13:00:34   Low-code development startup Genesis raises $200M round led by Tiger Global
https://siliconangle.com/2022/02/16/low-code-development-startup-genesis-raises-200m-round-led-tiger-global/

2022-02-16 12:45:00   Ireland Prepaid Card and Digital Wallet Market Report 2022: Market is Expected to Record a CAGR of 10.9%, Increasing from US$2.74 Billion in 2022 to Reach US$4.15 Billion by 2026
https://www.prnewswire.com/news-releases/ireland-prepaid-card-and-digital-wallet-market-report-2022-market-is-expected-to-record-a-cagr-of-10-9-increasing-from-us2-74-billion-in-2022-to-reach-us4-15-billion-by-2026--301483505.html

2022-02-16 12:45:00   Ireland Prepaid Card and Digital Wallet Market Report 2022: Market is Expected to Record a CAGR of 10.9%, Increasing from US$2.74 Billion in 2022 to Reach US$4.15 Billion by 2026
https://finance.yahoo.com/news/ireland-prepaid-card-digital-wallet-124500072.html

2022-02-16 12:38:49   Futures largely flat ahead of retail sales data, Fed minutes
https://www.reuters.com/business/futures-largely-flat-ahead-retail-sales-data-fed-minutes-2022-02-16/
```
