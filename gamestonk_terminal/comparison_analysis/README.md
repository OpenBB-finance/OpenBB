# COMPARISON ANALYSIS

This menu aims to compare a pre-loaded stock with similar companies, and the usage of the following commands along with an example will be exploited below.

* [get](#get)
  * get similar companies [Finviz, Finnhub, Polygon]
* [select](#select)
  * select similar companies
* [historical](#historical)
  * historical data comparison [Yahoo Finance]
* [hcorr](#hcorr)
  * historical correlation between similar companies [Yahoo Finance]
* [income](#income)
  * income financials comparison [Market Watch]
* [balance](#balance)
  * balance financials comparison [Market Watch]
* [cashflow](#cashflow)
  * cashflow financials comparison [Market Watch]
* [sentiment](#sentiment)
  * sentiment analysis comparison [FinBrain]
* [scorr](#scorr)
  * sentiment correlation between similar companies [FinBrain]
* [overview](#overview)
  * brief overview (e.g. Sector, Industry, Market Cap, Volume) [Finviz]
* [valuation](#valuation)
  * brief valuation (e.g. P/E, PEG, P/S, P/B, EPS this Y) [Finviz]
* [financial](#financial)
  * brief financial (e.g. Dividend, ROA, ROE, ROI, Earnings) [Finviz]
* [ownership](#ownership)
  * brief ownership (e.g. Float, Insider Own, Short Ratio) [Finviz]
* [performance](#performance)
  * brief performance (e.g. Perf Week, Perf YTD, Volatility M) [Finviz]
* [technical](#technical)
  * brief technical (e.g. Beta, SMA50, 52W Low, RSI, Change) [Finviz]
* [> po](portfolio_optimization/README.md)
  * **portfolio optimization for selected tickers**


## get <a name="get"></a>

```text
get [-s {polygon,finnhub,finviz}] [--nocountry]
```

Get similar companies to compare with. [Source: Finviz by default]

* -s : source that provides similar companies. Default: polygon.
* --nocountry : when getting similar companies from Finviz, we filter by same Industry, Sector and Country. However, if we don't want to filter by same country we can set this flag. For this flag to work, the `-p` flag can't be selected.

<img width="1005" alt="Captura de ecrã 2021-05-06, às 23 09 22" src="https://user-images.githubusercontent.com/25267873/117372489-864c4a80-aec1-11eb-87ec-ccd1a5a0a0e7.png">


## select <a name="select"></a>

```text
usage: select [-s L_SIMILAR]
```

Select similar companies, e.g. NIO,XPEV,LI

* -s : similar companies to compare with


## historical <a name="historical"></a>

```text
usage: historical [-s L_SIMILAR] [-a L_ALSO] [-t TYPE_CANDLE]
```

Historical price comparison between similar companies [Source: Yahoo Finance]

* -s : similar companies to compare with. Default pre-loaded ones.
* -a : apart from loaded similar companies also compare with.
* -t : type of candles: o-open, h-high, l-low, c-close, a-adjusted close. Default 'a'.

![historical](https://user-images.githubusercontent.com/25267873/110699590-ef2b8500-81e6-11eb-95e3-144793a83a80.png)

## hcorr <a name="hcorr"></a>

```text
usage: hcorr [-s L_SIMILAR] [-a L_ALSO] [-t TYPE_CANDLE]
```

Historical price correlation between similar companies [Source: Yahoo Finance]

* -s : similar companies to compare with. Default pre-loaded ones.
* -a : apart from loaded similar companies also compare with.
* -t : type of candles: o-open, h-high, l-low, c-close, a-adjusted close. Default 'a'.

![corr](https://user-images.githubusercontent.com/25267873/110699596-efc41b80-81e6-11eb-924f-8739058aa54e.png)


## income <a name="income"></a>

```text
usage: income [-s L_SIMILAR] [-a L_ALSO] [-t 31-Dec-2020/2017] [-q]
```

Income financials comparison between similar companies [Source: Market Watch]

* -s : similar companies to compare with. Default pre-loaded ones.
* -a : apart from loaded similar companies also compare with.
* -t : timeframe of earnings. Default: Last.
* -q : quarterly data instead of yearly. Default: False.

<img width="1007" alt="Captura de ecrã 2021-03-20, às 09 10 02" src="https://user-images.githubusercontent.com/25267873/111865162-4fe05d80-895d-11eb-8a0f-d7c2ba7700e2.png">


## balance <a name="balance"></a>

```text
usage: balance [-s L_SIMILAR] [-a L_ALSO] [-t 31-Dec-2020/2017] [-q]
```

Balance financials comparison between similar companies [Source: Market Watch]

* -s : similar companies to compare with. Default pre-loaded ones.
* -a : apart from loaded similar companies also compare with.
* -t : timeframe of earnings. Default: Last.
* -q : quarterly data instead of yearly. Default: False.

<img width="1014" alt="Captura de ecrã 2021-03-20, às 09 10 53" src="https://user-images.githubusercontent.com/25267873/111865168-5373e480-895d-11eb-960f-b919e338ab83.png">

## cashflow <a name="cashflow"></a>

```text
usage: cashflow [-s L_SIMILAR] [-a L_ALSO] [-t 31-Dec-2020/2017] [-q]
```

Cashflow financials comparison between similar companies [Source: Market Watch]

* -s : similar companies to compare with. Default pre-loaded ones.
* -a : apart from loaded similar companies also compare with.
* -t : timeframe of earnings. Default: Last.
* -q : quarterly data instead of yearly. Default: False.

<img width="1010" alt="Captura de ecrã 2021-03-20, às 09 12 59" src="https://user-images.githubusercontent.com/25267873/111865169-54a51180-895d-11eb-8d31-b499ab74854e.png">


## sentiment <a name="sentiment"></a>

```text
usage: sentiment [-s L_SIMILAR] [-a L_ALSO]
```

Sentiment analysis comparison [Source: FinBrain]

* -s : similar companies to compare with. Default pre-loaded ones.
* -a : apart from loaded similar companies also compare with.

<img width="754" alt="Captura de ecrã 2021-03-20, às 15 57 06" src="https://user-images.githubusercontent.com/25267873/111920503-45ba7e00-8a87-11eb-9a5c-aefb20793f7f.png">


## scorr <a name="scorr"></a>

```text
usage: scorr [-s L_SIMILAR] [-a L_ALSO] [-t TYPE_CANDLE]
```

Sentiment correlation between similar companies [Source: FinBrain]

* -s : similar companies to compare with. Default pre-loaded ones.
* -a : apart from loaded similar companies also compare with.

<img width="282" alt="Captura de ecrã 2021-03-20, às 15 57 01" src="https://user-images.githubusercontent.com/25267873/111920499-4521e780-8a87-11eb-9533-6844ba92f8f0.png">


## overview <a name="overview"></a>

```text
usage: overview [-s L_SIMILAR] [-a L_ALSO]
```

Prints screener data of similar companies. Some of the fields shown are: Sector, Industry, Market Cap, Volume. [Source: Finviz]

* -s : similar companies to compare with. Default pre-loaded ones.
* -a : apart from loaded similar companies also compare with.

<img width="1060" alt="overview" src="https://user-images.githubusercontent.com/25267873/114103686-7a209d80-98c1-11eb-9d6a-592f42dccbf1.png">


## valuation <a name="valuation"></a>

```text
usage: valuation [-s L_SIMILAR] [-a L_ALSO]
```

Prints screener data of similar companies. Some of the fields shown are: P/E, PEG, P/S, P/B, EPS this Y. [Source: Finviz]

* -s : similar companies to compare with. Default pre-loaded ones.
* -a : apart from loaded similar companies also compare with.

<img width="1067" alt="valuation" src="https://user-images.githubusercontent.com/25267873/114103689-7ab93400-98c1-11eb-95ed-8ceab347a8b4.png">


## financial <a name="financial"></a>

```text
usage: financial [-s L_SIMILAR] [-a L_ALSO]
```

Prints screener data of similar companies. Some of the fields shown are: Dividend, ROA, ROE, ROI, Earnings. [Source: Finviz]

* -s : similar companies to compare with. Default pre-loaded ones.
* -a : apart from loaded similar companies also compare with.

<img width="1049" alt="financial" src="https://user-images.githubusercontent.com/25267873/114103690-7ab93400-98c1-11eb-8f20-767ee23e1b37.png">


## ownership <a name="ownership"></a>

```text
usage: ownership [-s L_SIMILAR] [-a L_ALSO]
```

Prints screener data of similar companies. Some of the fields shown are: Float, Insider Own, Short Ratio. [Source: Finviz]

* -s : similar companies to compare with. Default pre-loaded ones.
* -a : apart from loaded similar companies also compare with.

<img width="1064" alt="ownership" src="https://user-images.githubusercontent.com/25267873/114103694-7bea6100-98c1-11eb-8261-49cca9b8a34c.png">


## performance <a name="performance"></a>

```text
usage: performance [-s L_SIMILAR] [-a L_ALSO]
```

Prints screener data of similar companies. Some of the fields shown are: Perf Week, Perf YTD, Volatility M. [Source: Finviz]

* -s : similar companies to compare with. Default pre-loaded ones.
* -a : apart from loaded similar companies also compare with.

<img width="1064" alt="performance" src="https://user-images.githubusercontent.com/25267873/114103691-7b51ca80-98c1-11eb-87d1-c816cda569bd.png">


## technical <a name="technical"></a>

```text
usage: technical [-s L_SIMILAR] [-a L_ALSO]
```

Prints screener data of similar companies. Some of the fields shown are: Beta, SMA50, 52W Low, RSI, Change. [Source: Finviz]

* -s : similar companies to compare with. Default pre-loaded ones.
* -a : apart from loaded similar companies also compare with.

<img width="1058" alt="technical" src="https://user-images.githubusercontent.com/25267873/114103696-7bea6100-98c1-11eb-93d9-66c732559c75.png">
