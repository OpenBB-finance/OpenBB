---
title: Due Diligence
---

## How to Use

The `DD` sub-module gives programmatic access to the same menu in the OpenBB Terminal. The functions, and a short description, are listed below.

|Path |Description |
|:----------------|----------------------------:|
|openbb.stocks.dd.analyst |Analyst Prices and Ratings |
|openbb.stocks.dd.arktrades |Ark Trades for the Ticker |
|openbb.stocks.dd.customer |List of Customers |
|openbb.stocks.dd.est |Earnings Estimates |
|openbb.stocks.dd.pt |Historical Price Targets |
|openbb.stocks.dd.rating |Daily Ratings |
|openbb.stocks.dd.rot |Historical Number of Analysts and Ratings |
|openbb.stocks.dd.sec |List of SEC Filings |
|openbb.stocks.dd.supplier |List of Suppliers |

Alternatively, the contents of the `dd` menu can be printed with:

```python
help(openbb.stocks.dd)
```

The data collected by these functions will compliment stock and company research, as well as broader macroeconomic research. If starting a script or notebook file from scratch, import the OpenBB SDK as Step 1.

```python
from openbb_terminal.sdk import openbb
```

## Examples

The examples here will assume that the import statements above are included at the top of the file.

### Customer

`openbb.stocks.dd.customer` returns a table of a company's publicly-listed customers and their changes in revenue and income.

```python
gtlb_customers = openbb.stocks.dd.customer('GTLB')

gtlb_customers
```

| TICKER   | Company Name                 | Rev. Y/Y     | Rev. Seq.    | Inc. Y/Y   | Inc. Seq.   |
|:---------|:-----------------------------|:-------------|:-------------|:-----------|:------------|
| GTLB     | Gitlab Inc.                  | -            | 15.6 %       | -          | -           |
| TICKER   | CUSTOMER NAME                | COST OF REV. | COST OF REV. | SG&A       | SG&A        |
| ALRM     | Alarm com Holdings Inc       | 6.47 %       | -2 %         | -44.1 %    | -55.87 %    |
| YOU      | Clear Secure Inc             | -            | -            | -          | -82.32 %    |
| EFX      | Equifax Inc                  | 10.94 %      | 0.07 %       | -7.61 %    | -3.69 %     |
| EVBG     | Everbridge Inc               | 16.95 %      | 6.64 %       | -25.27 %   | -35.71 %    |
| EVCM     | Evercommerce Inc             | 34.21 %      | 4.63 %       | -42.2 %    | -53.49 %    |
| RSKIA    | George Risk Industries Inc.  | 14.62 %      | -5.51 %      | -2.11 %    | -3.44 %     |
| INFY     | Infosys Limited              | 24.56 %      | -            | -          | -           |
| XM       | Qualtrics International Inc  | 67.05 %      | 6.91 %       | -43.49 %   | -44.79 %    |
| SEM      | Select Medical Holdings Corp | 7.41 %       | 0.23 %       | 4.24 %     | 5.96 %      |
| CXM      | Sprinklr Inc.                | 12.91 %      | 1.05 %       | 15.26 %    | 1.01 %      |
| SPT      | Sprout Social Inc            | 24.02 %      | 1.14 %       | -1.88 %    | -28.69 %    |
| TRU      | Transunion                   | -            | -            | 34.9 %     | 1.99 %      |

### Supplier

`openbb.stocks.dd.supplier` is the supply side to the `customer` function. It returns revenue, net income, net margin, and cash flow, for the companies feeding the ticker's supply chain.

```python
gtlb_suppliers = openbb.stocks.dd.supplier('GTLB')

gtlb_suppliers
```

| TICKER   | Company Name                                |   Revenue |   Net Income | Net Margin   |   Cash Flow |
|:---------|:--------------------------------------------|----------:|-------------:|:-------------|------------:|
| MSFT     | Microsoft Corporation                       |  50122    |     17556    | 35.03 %      |     8953    |
| DELL     | Dell Technologies Inc.                      |  26425    |       506    | 1.91 %       |    -1183    |
| ORCL     | Oracle Corporation                          |  21529    |      1548    | 7.19 %       |   -10935    |
| HPQ      | Hp Inc.                                     |  14664    |      1119    | 7.63 %       |      909    |
| IBM      | International Business Machines Corporation |  14107    |     -3196    | -            |      721    |
| CSCO     | Cisco Systems Inc                           |  13632    |      2670    | 19.59 %      |      213    |
| NCR      | Ncr Corp                                    |   1972    |        69    | 3.5 %        |       81    |
| FFIV     | F5 Inc                                      |    700.03 |        89.35 | 12.76 %      |      218.82 |
| PTC      | Ptc Inc                                     |    507.93 |       106.84 | 21.03 %      |      -50.16 |
| CGNT     | Cognyte Software Ltd                        |    474.04 |       -10.26 | -            |       43.56 |
| UIS      | Unisys Corp                                 |    461.2  |       -39.9  | -            |      -24.3  |
| NTNX     | Nutanix Inc.                                |    385.54 |      -150.99 | -            |       16.08 |
| ZS       | Zscaler Inc.                                |    372.17 |      -129.99 | -            |      418.32 |
| PAYC     | Paycom Software Inc                         |    334.17 |        52.15 | 15.61 %      |    -1618.67 |
| CDAY     | Ceridian Hcm Holding Inc                    |    315.6  |       -21    | -            |     -959.6  |
| TUYA     | Tuya Inc                                    |    302.08 |      -175.42 | -            |      805.62 |
| NET      | Cloudflare Inc                              |    253.86 |       -42.55 | -            |       -4.76 |
| PCTY     | Paylocity Holding Corporation               |    253.28 |        30.35 | 11.98 %      |    -1836.35 |
| ZI       | Zoominfo Technologies Inc                   |    251.7  |        17.9  | 7.11 %       |       53.9  |
| PATH     | Uipath Inc.                                 |    242.22 |      -120.38 | -            |      -71.86 |
| BL       | Blackline Inc                               |    134.27 |       -18.99 | -            |      -17.95 |
| WK       | Workiva Inc                                 |    132.85 |       -29.69 | -            |       80.07 |
| PYCR     | Paycor Hcm Inc                              |    118.3  |       -29.05 | -            |     -915.72 |
| APPN     | Appian Corporation                          |    117.88 |       -44    | -            |      -25.24 |
| AVID     | Avid Technology Inc                         |    102.99 |        12.02 | 11.67 %      |      -13.12 |
| GTLB     | Gitlab Inc.                                 |    101.04 |       -61.5  | -            |     -476.73 |
| ATTU     | Attunity Ltd                                |     86.25 |         5.96 | 6.91 %       |      -17.32 |
| ESMT     | Engagesmart Inc                             |     78.8  |         6.77 | 8.59 %       |       19.25 |
| FROG     | Jfrog Ltd                                   |     71.99 |       -23.55 | -            |       -1.24 |
| DWCH     | Datawatch Corp                              |     11.59 |        -2.27 | -            |        0.15 |
| GSB      | Globalscape Inc                             |     10.03 |         3.5  | 34.9 %       |        3.17 |
| STVVY    | China Digital Tv Holding Co., Ltd.          |      6.2  |        -4.1  | -            |      -92.87 |
| FALC     | Falconstor Software Inc                     |      3.06 |         0.6  | 19.64 %      |       -0.14 |
| ZRFY     | Zerify Inc                                  |      0.02 |        -1.25 | -            |       -0.32 |

### ROT

`openbb.stocks.dd.rot` returns a table with the number of analyst recommendations for each score, updated monthly.

```python
gtlb_rot = openbb.stocks.dd.rot('GTLB')

gtlb_rot
```

|    |   buy |   hold | period     |   sell |   strongBuy |   strongSell | symbol   |
|---:|------:|-------:|:-----------|-------:|------------:|-------------:|:---------|
|  0 |    14 |      2 | 2022-11-01 |      0 |           4 |            0 | GTLB     |
|  1 |    14 |      2 | 2022-10-01 |      0 |           4 |            0 | GTLB     |
|  2 |    13 |      1 | 2022-09-01 |      0 |           4 |            0 | GTLB     |
|  3 |    13 |      1 | 2022-08-01 |      0 |           4 |            0 | GTLB     |

### Analyst

Returns a DataFrame of analyst price targets, and their coverage history.

```python
gtlb_pt = openbb.stocks.dd.analyst('GTLB')

gtlb_pt
```

| date       | category   | analyst          | rating                |   target |   target_from |   target_to |
|:-----------|:-----------|:-----------------|:----------------------|---------:|--------------:|------------:|
| 2022-09-22 | Initiated  | MoffettNathanson | Buy                   |      104 |           nan |         nan |
| 2022-09-01 | Downgrade  | JP Morgan        | Overweight -> Neutral |       63 |           nan |         nan |
| 2022-07-07 | Initiated  | Needham          | Buy                   |       70 |           nan |         nan |
| 2022-06-27 | Upgrade    | Goldman          | Neutral -> Buy        |      nan |            69 |          80 |
| 2022-06-09 | Initiated  | Scotiabank       | Sector Outperform     |       62 |           nan |         nan |

### SEC

`openbb.stocks.dd.sec` gets a DataFrame of the recent SEC filings submitted by the company and a link to view each one.

```python
gtlb_sec = openbb.stocks.dd.sec('GTLB')

gtlb_sec
```

| Filing Date   | Document Date   | Type     | Category                | Amended   | Link                                                                                  |
|:--------------|:----------------|:---------|:------------------------|:----------|:--------------------------------------------------------------------------------------|
| 09/07/2022    | 07/31/2022      | 10-Q     | Quarterly Reports       |           | https://www.marketwatch.com/investing/stock/gtlb/financials/secfilings?docid=16067993 |
| 09/06/2022    | 09/06/2022      | 8-K      | Special Events          |           | https://www.marketwatch.com/investing/stock/gtlb/financials/secfilings?docid=16066715 |
| 07/08/2022    | N/A             | SC 13G/A | Institutional Ownership | *         | https://www.marketwatch.com/investing/stock/gtlb/financials/secfilings?docid=15940277 |
| 06/23/2022    | 06/17/2022      | 8-K      | Special Events          |           | https://www.marketwatch.com/investing/stock/gtlb/financials/secfilings?docid=15906497 |
| 06/07/2022    | 04/30/2022      | 10-Q     | Quarterly Reports       |           | https://www.marketwatch.com/investing/stock/gtlb/financials/secfilings?docid=15877097 |
| 06/06/2022    | 06/06/2022      | 8-K      | Special Events          |           | https://www.marketwatch.com/investing/stock/gtlb/financials/secfilings?docid=15875737 |
| 05/13/2022    | N/A             | SC 13G   | Institutional Ownership |           | https://www.marketwatch.com/investing/stock/gtlb/financials/secfilings?docid=15814288 |
| 05/05/2022    | 01/31/2022      | DEF 14A  | Proxy Statement         |           | https://www.marketwatch.com/investing/stock/gtlb/financials/secfilings?docid=15792144 |
| 04/11/2022    | N/A             | SC 13G/A | Institutional Ownership | *         | https://www.marketwatch.com/investing/stock/gtlb/financials/secfilings?docid=15724191 |
| 04/11/2022    | N/A             | S-8      | Registration Statement  |           | https://www.marketwatch.com/investing/stock/gtlb/financials/secfilings?docid=15723998 |
| 04/08/2022    | 01/31/2022      | 10-K     | Annual Reports          |           | https://www.marketwatch.com/investing/stock/gtlb/financials/secfilings?docid=15723401 |
continued...

### EST

`openbb.stocks.dd.est` returns a Tuple with forward earnings and revenue estimates.

```python
year_estimates_df,qtr_earnings_df,qtr_revenue_df = openbb.stocks.dd.est('GTLB')

year_estimates_df
```

| YEARLY ESTIMATES               | 2022   | 2023   | 2024   | 2025    | 2026      | 2027   |
|:-------------------------------|:-------|:-------|:-------|:--------|:----------|:-------|
| Revenue                        | 245    | 414    | 586    | 814     | 1,044     | 1,305  |
| Dividend                       | 0.00   | -      | 0.00   | 0.00    | -         | -      |
| Dividend Yield (in %)          | -      | -      | -      | -       | -         | -      |
| EPS                            | -1.40  | -0.65  | -0.65  | -0.35   | -0.02     | 0.27   |
| P/E Ratio                      | -28.07 | -60.24 | -60.97 | -113.57 | -1,970.00 | 145.93 |
| EBIT                           | -103   | -109   | -101   | -62     | -17       | 30     |
| EBITDA                         | -99    | -123   | -124   | -51     | -10       | 40     |
| Net Profit                     | -152   | -151   | -177   | -100    | -4        | 50     |
| Net Profit Adjusted            | -114   | -98    | -99    | -55     | -4        | 51     |
| Pre-Tax Profit                 | -121   | -100   | -96    | -53     | -4        | 48     |
| Net Profit (Adjusted)          | -134   | -198   | -218   | -70     | -         | -      |
| EPS (Non-GAAP) ex. SOE         | -1.55  | -0.65  | -0.63  | -0.48   | -         | -      |
| EPS (GAAP)                     | -1.90  | -1.34  | -1.56  | -1.20   | -         | -      |
| Gross Income                   | 217    | 368    | 509    | 692     | 911       | 1,134  |
| Cash Flow from Investing       | -100   | -486   | -9     | -12     | -14       | -17    |
| Cash Flow from Operations      | -75    | -67    | -31    | 28      | 120       | 251    |
| Cash Flow from Financing       | 561    | 80     | 8      | 0       | -         | -      |
| Cash Flow per Share            | -1.06  | -0.52  | -0.23  | -0.08   | -         | -      |
| Free Cash Flow                 | -73    | -77    | -39    | 37      | 106       | 234    |
| Free Cash Flow per Share       | -0.96  | -0.56  | -0.22  | -       | -         | -      |
| Book Value per Share           | 7.16   | 5.11   | 4.52   | 4.10    | -         | -      |
| Net Debt                       | -798   | -403   | -372   | -460    | -         | -      |
| Research & Development Exp.    | 90     | 120    | 158    | 208     | 244       | 292    |
| Capital Expenditure            | 0      | 6      | 8      | 13      | -         | -      |
| Selling, General & Admin. Exp. | 230    | 361    | 473    | 509     | -         | -      |
| Shareholder’s Equity           | 831    | 729    | 649    | 611     | 589       | 639    |
| Total Assets                   | 1,093  | 1,105  | 1,159  | 1,397   | 1,658     | 2,027  |

### Snippet

Below is a way to quickly collect the eight DataFrames created in the examples above, change the ticker variable to look at other US-listed companies.

```python
from openbb_terminal.sdk import openbb
import pandas as pd

ticker: str = 'GTLB'

customers_df = openbb.stocks.dd.customer(ticker, limit = 200)
suppliers_df = openbb.stocks.dd.supplier(ticker, limit = 200)
rot_df = openbb.stocks.dd.rot(ticker)
pt_df = openbb.stocks.dd.analyst(ticker)
sec_df = openbb.stocks.dd.sec(ticker)
year_estimates_df,qtr_earnings_df,qtr_revenue_df = openbb.stocks.dd.est(ticker)
dd_df:object = pd.Series(data= [qtr_earnings_df,qtr_revenue_df,year_estimates_df,customers_df,suppliers_df,rot_df,pt_df,sec_df])

dd_df[0]
```

| QUARTER EARNINGS ESTIMATES   | Previous Quarter   | Current Quarter   | Next Quarter   | Current Year    | Next Year       |
|:-----------------------------|:-------------------|:------------------|:---------------|:----------------|:----------------|
| Date                         | -                  | -                 | -              | ending 01/31/22 | ending 01/31/23 |
| No. of Analysts              | -                  | -                 | -              | 10              | 13              |
| Average Estimate             | -                  | -                 | -              | -1.404 USD      | -0.654 USD      |
| Year Ago                     | -                  | -                 | -              | -               | -1.404 USD      |
| Publish Date                 | -                  | -                 | -              | -               | -               |
