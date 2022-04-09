```
usage: sec [-l LIMIT] [-h] [--export {csv,json,xlsx}]
```

Prints SEC filings of the company. The following fields are expected: Filing Date, Document Date, Type, Category, Amended, and Link. [Source: Market Watch]

```
optional arguments:
  -l LIMIT, --limit LIMIT
                        number of latest SEC filings.
  -h, --help            show this help message
  --export {csv,json,xlsx}
                        Export raw data into csv, json, xlsx
```

Example:
```
2022 Feb 16, 04:37 (✨) /stocks/dd/ $ sec -l 10
                                                                             SEC Filings
┏━━━━━━━━━━━━┳━━━━━━━━━━━━━━━┳━━━━━━━━━━┳━━━━━━━━━━━━━━━━━━━━━━━━━┳━━━━━━━━━┳━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓
┃            ┃ Document Date ┃ Type     ┃ Category                ┃ Amended ┃ Link                                                                                  ┃
┡━━━━━━━━━━━━╇━━━━━━━━━━━━━━━╇━━━━━━━━━━╇━━━━━━━━━━━━━━━━━━━━━━━━━╇━━━━━━━━━╇━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┩
│ 02/15/2022 │ N/A           │ SC 13G/A │ Institutional Ownership │ *       │ https://www.marketwatch.com/investing/stock/tsla/financials/secfilings?docid=15572277 │
├────────────┼───────────────┼──────────┼─────────────────────────┼─────────┼───────────────────────────────────────────────────────────────────────────────────────┤
│ 02/14/2022 │ N/A           │ SC 13G/A │ Institutional Ownership │ *       │ https://www.marketwatch.com/investing/stock/tsla/financials/secfilings?docid=15565323 │
├────────────┼───────────────┼──────────┼─────────────────────────┼─────────┼───────────────────────────────────────────────────────────────────────────────────────┤
│ 02/10/2022 │ N/A           │ SC 13G/A │ Institutional Ownership │ *       │ https://www.marketwatch.com/investing/stock/tsla/financials/secfilings?docid=15548625 │
├────────────┼───────────────┼──────────┼─────────────────────────┼─────────┼───────────────────────────────────────────────────────────────────────────────────────┤
│ 02/08/2022 │ N/A           │ SC 13G   │ Institutional Ownership │         │ https://www.marketwatch.com/investing/stock/tsla/financials/secfilings?docid=15541156 │
├────────────┼───────────────┼──────────┼─────────────────────────┼─────────┼───────────────────────────────────────────────────────────────────────────────────────┤
│ 02/07/2022 │ 12/31/2021    │ 10-K     │ Annual Reports          │         │ https://www.marketwatch.com/investing/stock/tsla/financials/secfilings?docid=15534769 │
├────────────┼───────────────┼──────────┼─────────────────────────┼─────────┼───────────────────────────────────────────────────────────────────────────────────────┤
│ 01/26/2022 │ 01/26/2022    │ 8-K      │ Special Events          │         │ https://www.marketwatch.com/investing/stock/tsla/financials/secfilings?docid=15502788 │
├────────────┼───────────────┼──────────┼─────────────────────────┼─────────┼───────────────────────────────────────────────────────────────────────────────────────┤
│ 01/03/2022 │ 01/02/2022    │ 8-K      │ Special Events          │         │ https://www.marketwatch.com/investing/stock/tsla/financials/secfilings?docid=15453642 │
├────────────┼───────────────┼──────────┼─────────────────────────┼─────────┼───────────────────────────────────────────────────────────────────────────────────────┤
│ 12/01/2021 │ 12/01/2021    │ 8-K      │ Special Events          │         │ https://www.marketwatch.com/investing/stock/tsla/financials/secfilings?docid=15394282 │
├────────────┼───────────────┼──────────┼─────────────────────────┼─────────┼───────────────────────────────────────────────────────────────────────────────────────┤
│ 10/25/2021 │ 09/30/2021    │ 10-Q     │ Quarterly Reports       │         │ https://www.marketwatch.com/investing/stock/tsla/financials/secfilings?docid=15297229 │
├────────────┼───────────────┼──────────┼─────────────────────────┼─────────┼───────────────────────────────────────────────────────────────────────────────────────┤
│ 10/20/2021 │ 10/20/2021    │ 8-K      │ Special Events          │         │ https://www.marketwatch.com/investing/stock/tsla/financials/secfilings?docid=15291361 │
└────────────┴───────────────┴──────────┴─────────────────────────┴─────────┴───────────────────────────────────────────────────────────────────────────────────────┘
```
