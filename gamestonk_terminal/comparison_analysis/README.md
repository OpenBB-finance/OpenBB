# COMPARISON ANALYSIS

This menu aims to compare a pre-loaded stock with similar companies, and the usage of the following commands along with an example will be exploited below.

* [get](#get)
  * get similar companies [Polygon]
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
* [scorr](#corr)
  * sentiment correlation between similar companies [FinBrain]


## get <a name="get"></a>

```text
get
```

Get similar companies to compare with. [Source: Polygon]


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
usage: corr [-s L_SIMILAR] [-a L_ALSO] [-t TYPE_CANDLE]
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
usage: corr [-s L_SIMILAR] [-a L_ALSO] [-t TYPE_CANDLE]
```

Sentiment correlation between similar companies [Source: FinBrain]

* -s : similar companies to compare with. Default pre-loaded ones.
* -a : apart from loaded similar companies also compare with.

<img width="282" alt="Captura de ecrã 2021-03-20, às 15 57 01" src="https://user-images.githubusercontent.com/25267873/111920499-4521e780-8a87-11eb-9533-6844ba92f8f0.png">


