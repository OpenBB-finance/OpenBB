```text
usage: get [-u] [-n] [-l LIMIT] [-h] [--source {Finviz,Polygon,Finnhub}]
```

Get similar companies from selected data source (default: [Finviz](https://finviz.com)) to compare with.

```
optional arguments:
  -u, --us_only         Show only stocks from the US stock exchanges. Works only with Polygon (default: False)
  -n, --nocountry       Similar stocks from finviz using only Industry and Sector. (default: False)
  -l LIMIT, --limit LIMIT
                        Limit of stocks to retrieve. (default: 10)
  -h, --help            show this help message (default: False)
  --source {Finviz,Polygon,Finnhub}
                        Data source to select from (default: Finviz)
```
<img size="1400" alt="Feature Screenshot - get" src="https://user-images.githubusercontent.com/85772166/142900078-9872e832-016a-4966-bbc3-0075928c7db8.png">

