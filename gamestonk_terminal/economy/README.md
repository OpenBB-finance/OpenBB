# ECONOMY

This menu aims to assess economy data, and the usage of the following commands along with an example will be exploited below.

* [feargreed](#feargreed)
    * CNN Fear Greed Index from https://money.cnn.com/data/fear-and-greed/
* [events](#events)
    * economic impact events [Finnhub]
* [fred](#fred)
    * display customized FRED from https://fred.stlouisfed.org
* [vixcls](#vixcls)
    * Volatility Index
* [gdp](#gdp)
    * Gross Domestic Product
* [unrate](#unrate)
    * Unemployment Rate
* [dgs1](#dgs1)
    * 1-Year Treasury Constant Maturity Rate
* [dgs5](#dgs5)
    * 5-Year Treasury Constant Maturity Rate
* [dgs10](#dgs10)
    * 10-Year Treasury Constant Maturity Rate
* [dgs30](#dgs30)
    * 30-Year Treasury Constant Maturity Rate
* [mortgage30us](#mortgage30us)
    * 30-Year Fixed Rate Mortgage Average
* [fedfunds](#fedfunds)
    * Effective Federal Funds Rate
* [aaa](#aaa)
    * Moody's Seasoned AAA Corporate Bond Yield
* [dexcaus](#dexcaus)
    * Canada / U.S. Foreign Exchange Rate (CAD per 1 USD)

[WSJ](#wsj)
* [overview](#overview)
  * Get market overview
* [indices](#indices)
  * Get us major indices overview
* [futures](#futures)
  * Get top futures overview
* [us_bonds](#us_bonds)
  * Get us bonds overview
* [gl_bonds](#gl_bonds)
  * Get global bonds overview
* [currencies](#currencies)
  * Get global currency overview


## feargreed <a name="feargreed"></a>
```text
usage: feargreed [-i {jbd,mv,pco,mm,sps,spb,shd,index}]
```

Display CNN Fear And Greed Index from https://money.cnn.com/data/fear-and-greed/.
* -i : CNN Fear And Greed indicator or index. From Junk Bond Demand, Market Volatility, Put and Call Options, Market Momentum Stock Price, Strength, Stock Price Breadth, Safe Heaven Demand, and Index. Default: None, shows all.

![feargreed](https://user-images.githubusercontent.com/25267873/122684285-7338d400-d1fc-11eb-8702-d409d96a2672.png)

<img width="962" alt="Captura de ecrã 2021-06-20, às 19 18 12" src="https://user-images.githubusercontent.com/25267873/122684256-4a184380-d1fc-11eb-939c-d8007310324d.png">


## events <a name="events"></a>
```text
usage: events [-c {NZ,AU,ERL,CA,EU,US,JP,CN,GB,CH}] [-i {low,medium,high,all}] [-n NUM]
```

Output economy impact calendar impact events. [Source: https://finnhub.io]

* -c : Country from where to get economy calendar impact events, between NZ,AU,ERL,CA,EU,US,JP,CN,GB,CH. Default: US.
* -i : Impact of the economy event, between low,medium,high,all. Default: all.
* -n : Number economy calendar impact events to display. Default: 10.

<img width="1055" alt="Captura de ecrã 2021-05-02, às 19 51 47" src="https://user-images.githubusercontent.com/25267873/116824200-def9ab80-ab80-11eb-948a-48a94f662b53.png">


## fred <a name="fred"></a>
```text
usage: fred [-i SERIES_ID] [-s START_DATE] [-t]
```

Display customized Federal Reserve Economic Data (FRED) from https://fred.stlouisfed.org.

* -i : FRED Series ID from https://fred.stlouisfed.org.
* -s : Starting date (YYYY-MM-DD) of data. Default: 2019-01-01.
* -t : Only output text data.


## vixcls <a name="vixcls"></a>
```text
usage: vixcls [-s START_DATE] [-t]
```

Volatility Index

* -s : Starting date (YYYY-MM-DD) of data. Default: 2019-01-01.
* -t : Only output text data.

![vixcls](https://user-images.githubusercontent.com/25267873/116769167-160d7700-aa32-11eb-8874-3b864908c9c2.png)


## gdp <a name="gdp"></a>
```text
usage: gdp [-s START_DATE] [-t]
```

Gross Domestic Product

* -s : Starting date (YYYY-MM-DD) of data. Default: 2019-01-01.
* -t : Only output text data.

![gdp](https://user-images.githubusercontent.com/25267873/116769162-14dc4a00-aa32-11eb-886a-b5368146ed37.png)


## unrate <a name="unrate"></a>
```text
usage: unrate [-s START_DATE] [-t]
```

Unemployment Rate

* -s : Starting date (YYYY-MM-DD) of data. Default: 2019-01-01.
* -t : Only output text data.

![unrate](https://user-images.githubusercontent.com/25267873/116769161-14dc4a00-aa32-11eb-91f3-a0f80d687a12.png)


## dgs1 <a name="dgs1"></a>
```text
usage: dgs1 [-s START_DATE] [-t]
```

1-year Treasury Constant Maturity Rate

* -s : Starting date (YYYY-MM-DD) of data. Default: 2019-01-01.
* -t : Only output text data.

![dgs1](https://user-images.githubusercontent.com/25267873/116769166-160d7700-aa32-11eb-9247-78156af4d527.png)


## dgs5 <a name="dgs5"></a>
```text
usage: dgs5 [-s START_DATE] [-t]
```

5-year Treasury Constant Maturity Rate

* -s : Starting date (YYYY-MM-DD) of data. Default: 2019-01-01.
* -t : Only output text data.

![dgs5](https://user-images.githubusercontent.com/25267873/116769165-1574e080-aa32-11eb-96ee-c57728d8f57c.png)


## dgs10 <a name="dgs10"></a>
```text
usage: dgs10 [-s START_DATE] [-t]
```

10-year Treasury Constant Maturity Rate

* -s : Starting date (YYYY-MM-DD) of data. Default: 2019-01-01.
* -t : Only output text data.

![dgs10](https://user-images.githubusercontent.com/25267873/116769164-1574e080-aa32-11eb-93a0-3b8a2b7cb3d2.png)


## dgs30 <a name="dgs30"></a>
```text
usage: dgs30 [-s START_DATE] [-t]
```

30-year Treasury Constant Maturity Rate

* -s : Starting date (YYYY-MM-DD) of data. Default: 2019-01-01.
* -t : Only output text data.

![dgs30](https://user-images.githubusercontent.com/25267873/116769159-13ab1d00-aa32-11eb-8c3d-e53c8d1f1a19.png)


## mortgage30us <a name="mortgage30us"></a>
```text
usage: mortgage30us [-s START_DATE] [-t]
```

30-year Fixed Rate Mortgage Average

* -s : Starting date (YYYY-MM-DD) of data. Default: 2019-01-01.
* -t : Only output text data.

![mortgage30us](https://user-images.githubusercontent.com/25267873/116769157-13128680-aa32-11eb-8826-ccb2e6ae764e.png)


## fedfunds <a name="fedfunds"></a>
```text
usage: fedfunds [-s START_DATE] [-t]
```

Effective Federal Funds Rate

* -s : Starting date (YYYY-MM-DD) of data. Default: 2019-01-01.
* -t : Only output text data.

![fedfunds](https://user-images.githubusercontent.com/25267873/116769158-13ab1d00-aa32-11eb-9dc2-8296bc4f7e2c.png)


## aaa <a name="aaa"></a>
```text
usage: aaa [-s START_DATE] [-t]
```

Moody's Seasoned AAA Corporate Bond Yield

* -s : Starting date (YYYY-MM-DD) of data. Default: 2019-01-01.
* -t : Only output text data.

![aaa](https://user-images.githubusercontent.com/25267873/116769160-1443b380-aa32-11eb-84a8-036e15b47c9b.png)


## dexcaus <a name="dexcaus"></a>
```text
usage: dexcaus [-s START_DATE] [-t]
```

Canada / U.S. Foreign Exchange Rate (CAD per 1 USD)

* -s : Starting date (YYYY-MM-DD) of data. Default: 2019-01-01.
* -t : Only output text data.

![dexcaus](https://user-images.githubusercontent.com/25267873/116769155-10b02c80-aa32-11eb-8ece-d8e92b8df1af.png)

# WSJ <a name="wsj"></a>
The following functions are meant to take the information from the [WSJ Market Data Page](https://www.wsj.com/market-data)

## overview <a name="overview"></a>
```python
usage: overview
```
Market overview

## indices <a name="indices"></a>
```python
usage: indices
```
US indices overview

## futures <a name="futures"></a>
```python
usage: futures
```
Top futures/commodities overview

## us_bonds <a name="us_bonds"></a>
```python
usage: us_bonds
```
US bonds overview

## gl_bonds <a name="gl_bonds"></a>
```python
usage: gl_bonds
```
Global bonds overview

## currencies <a name="currencies"></a>
```python
usage: currencies
```
Global currencies overview
