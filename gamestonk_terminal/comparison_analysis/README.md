# COMPARISON ANALYSIS

This menu aims to compare a pre-loaded stock with similar companies, and the usage of the following commands along with an example will be exploited below.

* [get](#get)
  * get similar companies [Polygon]
* [select](#select)
  * select similar companies
* [historical](#historical)
  * historical data comparison [Yahoo Finance]
* [corr](#corr)
  * correlation between similar companies [Yahoo Finance]


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

## corr <a name="corr"></a>

```text
usage: corr [-s L_SIMILAR] [-a L_ALSO] [-t TYPE_CANDLE]
```

Historical price comparison between similar companies [Source: Yahoo Finance]

* -s : similar companies to compare with. Default pre-loaded ones.
* -a : apart from loaded similar companies also compare with.
* -t : type of candles: o-open, h-high, l-low, c-close, a-adjusted close. Default 'a'.

![corr](https://user-images.githubusercontent.com/25267873/110699596-efc41b80-81e6-11eb-924f-8739058aa54e.png)
