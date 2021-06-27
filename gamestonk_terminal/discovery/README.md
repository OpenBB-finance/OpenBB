# DISCOVER STOCKS

This menu aims to discover new stocks, and the usage of the following commands along with an example will be exploited below.

* [ipo](#ipo)
  * past and future IPOs [Finnhub]
* [map](#map)
  * S&P500 index stocks map [Finviz]
* [rtp_sectors](#rtp_sectors)
  * real-time performance sectors [Alpha Vantage]
* [gainers](#gainers)
  * show latest top gainers [Yahoo Finance]
* [losers](#losers)
  * show latest top losers [Yahoo Finance]
* [orders](#orders)
  * orders by Fidelity Customers [Fidelity]
* [ark_orders](#ark_orders)
  * orders by ARK Investment Management LLC [https://cathiesark.com]
* [up_earnings](#up_earnings)
  * upcoming earnings release dates [Seeking Alpha]
* [high_short](#high_short)
  * show top high short interest stocks of over 20% ratio [www.highshortinterest.com]
* [low_float](#low_float)
  * show low float stocks under 10M shares float [www.lowfloat.com]
* [simply_wallst](#simply_wallst)
  * Simply Wall St. research data [Simply Wall St.]
* [spachero](#spachero)
  * great website for SPACs research [SpacHero]
* [uwhales](#uwhales)
  * good website for SPACs research [UnusualWhales]
* [valuation](#valuation)
  * valuation of sectors, industry, country [Finviz]
* [performance](#performance)
  * performance of sectors, industry, country [Finviz]
* [spectrum](#spectrum)
  * spectrum of sectors, industry, country [Finviz]
* [latest](#latest)
  * latest news [Seeking Alpha]
* [trending](#trending)
  * trending news [Seeking Alpha]
* [ratings](#ratings)
  * top ratings updates [MarketBeat]
* [darkpool](#darkpool)
  * dark pool tickers with growing activity [FINRA]
* [darkshort](#darkshort)
  * dark pool short position [Stockgrid]
* [shortvol](#shortvol)
  * short interest and days to cover [Stockgrid]

## ipo <a name="ipo"></a>

```shell
usage: ipo [-p PAST_DAYS] [-f FUTURE_DAYS]
```

Past and future IPOs. [Source: https://finnhub.io]

* -p : Number of past days to look for IPOs. Default 0.
* -f : Number of future days to look for IPOs. Default 10.

<img width="1005" alt="Captura de ecrã 2021-05-03, às 12 54 44" src="https://user-images.githubusercontent.com/25267873/116873168-1e6ed900-ac0f-11eb-9d80-dddc8a754885.png">


## map <a name="map"></a>

```shell
usage: map [-p {1d,1w,1m,3m,6m,1y}] [-t {sp500,world,full,etf}]
```

Performance index stocks map categorized by sectors and industries. Size represents market cap. Opens web-browser. [Source: Finviz]

* -p : Performance period. Default 1 day.
* -t : Map filter type. Default S&P500.

![map_filter](https://user-images.githubusercontent.com/25267873/108570986-032a4800-7307-11eb-8c8d-f62409c11e06.png)

## rtp_sectors <a name="rtp_sectors"></a>

```shell
usage: rtp_sectors
```

Real-time and historical sector performances calculated from S&P500 incumbents. Pops plot in terminal. [Source: Alpha Vantage]

![sectors](https://user-images.githubusercontent.com/25267873/108572267-d297dd80-7309-11eb-863b-20cfe3012c30.png)

## gainers <a name="gainers"></a>

```shell
usage: gainers [-n {1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20,21,22,23,24}]
```

Print up to 25 top ticker gainers in terminal. [Source: Yahoo Finance]

* -n : Number of the top gainers stocks to retrieve. Default 5.

<img width="935" alt="Captura de ecrã 2021-02-20, às 11 46 09" src="https://user-images.githubusercontent.com/25267873/108594319-46b99c00-7371-11eb-877e-ef75d3ba472b.png">

## losers <a name="losers"></a>

```shell
usage: losers [-n {1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20,21,22,23,24}]
```

Print up to 25 top ticker losers in terminal. [Source: Yahoo Finance]

* -n : Number of the top losers stocks to retrieve. Default 5.

<img width="993" alt="Captura de ecrã 2021-03-14, às 20 23 21" src="https://user-images.githubusercontent.com/25267873/111083099-a421b280-8503-11eb-9bb0-c728ce1e313f.png">

## orders <a name="orders"></a>

```shell
usage: orders [-n N_NUM]
```

Orders by Fidelity customers. Information shown in the table below is based on the volume of orders entered on the "as of" date shown. Securities identified are not recommended or endorsed by Fidelity and are displayed for informational purposes only. [Source: Fidelity]

* -n : Number of top ordered stocks to be printed. Default 10.

<img width="945" alt="Captura de ecrã 2021-02-20, às 11 45 43" src="https://user-images.githubusercontent.com/25267873/108594318-45886f00-7371-11eb-919f-fd1bce6d4001.png">

## ark_orders <a name="ark_orders"></a>

```shell
usage: ark_orders [-n N_NUM]
```

 Orders by ARK Investment Management LLC - https://ark-funds.com/. [Source: https://cathiesark.com]

* -n : Last N orders to be printed. Default 20.

<img width="957" alt="Captura de ecrã 2021-03-10, às 21 36 38" src="https://user-images.githubusercontent.com/25267873/110701322-ef2c8480-81e8-11eb-85a2-7ebfa3fa0680.png">


## up_earnings <a name="up_earnings"></a>

```shell
usage: up_earnings [-p N_PAGES] [-n N_NUM]
```

Print upcoming earnings release dates. [Source: Seeking Alpha]

* -p : Number of pages to read upcoming earnings from in Seeking Alpha website. Default 10.
* -n : Number of upcoming earnings release dates to print. Default 3.

<img width="933" alt="Captura de ecrã 2021-02-20, às 11 45 24" src="https://user-images.githubusercontent.com/25267873/108594317-45886f00-7371-11eb-85e6-03d839d421b3.png">

## high_short <a name="high_short"></a>

```shell
usage: high_short [-n N_NUM]
```

Print top stocks being more heavily shorted. HighShortInterest.com provides a convenient sorted database of stocks which have a short interest of over 20 percent. Additional key data such as the float, number of outstanding shares, and company industry is displayed. Data is presented for the Nasdaq Stock Market, the New York Stock Exchange, and the American Stock Exchange. Stocks with high short interest are often very volatile and are well known for making explosive upside moves (known as a short squeeze). [Source: www.highshortinterest.com]

* -n : Number of top stocks to print

<img width="940" alt="Captura de ecrã 2021-02-20, às 11 45 02" src="https://user-images.githubusercontent.com/25267873/108594316-45886f00-7371-11eb-8ded-94fbe28ac84c.png">

## low_float <a name="low_float"></a>

```shell
usage: low_float [-n N_NUM]
```

Print top stocks with lowest float. LowFloat.com provides a convenient sorted database of stocks which have a float of under 10 million shares. Additional key data such as the number of outstanding shares, short interest, and company industry is displayed. Data is presented for the Nasdaq Stock Market, the New York Stock Exchange, the American Stock Exchange, and the Over the Counter Bulletin Board. [Source: www.lowfloat.com]

* -n : Number of top stocks to print

<img width="942" alt="Captura de ecrã 2021-02-20, às 11 44 39" src="https://user-images.githubusercontent.com/25267873/108594315-44efd880-7371-11eb-9be7-7ae02999fd09.png">

## simply_wallst <a name="simply_wallst"></a>

```shell
usage: simply_wallst [-i {any,automobiles,banks,capital-goods,commercial-services,consumer-durables,consumer-services,diversified-financials,energy,consumer-retailing,food-beverage-tobacco,healthcare,household,insurance,materials,media,pharmaceuticals-biotech,real-estate,retail,semiconductors,software,tech,telecom,transportation,utilities}]
```

Simply Wall Street Research. Opens web browser. Although this does not require an API key, it requires a subscription to the website by the user (there's a 14 days free trial). [Source: Simply Wall St.]

* -i : Industry of interest

<img width="1200" alt="sw" src="https://user-images.githubusercontent.com/25267873/108576534-dfbac980-7315-11eb-9350-254fb9b64773.png">

## spachero <a name="spachero"></a>

```shell
usage: spachero
```

Great website for SPACs research. [Source: www.spachero.com]

<img width="1265" alt="Captura de ecrã 2021-02-20, às 01 12 14" src="https://user-images.githubusercontent.com/25267873/108577430-f282cd80-7318-11eb-888b-82dcf90d4f32.png">

## uwhales <a name="uwhales"></a>

```shell
usage: uwhales
```

Good website for SPACs research. [Source: www.unusualwhales.com]

<img width="1247" alt="Captura de ecrã 2021-02-20, às 11 38 54" src="https://user-images.githubusercontent.com/25267873/108594176-47056780-7370-11eb-8f2d-5972c8634974.png">

## valuation <a name="valuation"></a>

```shell
usage: valuation [-g Sector,Industry,Industry (Basic Materials),Industry (Communication Services),
Industry (Consumer Cyclical),Industry (Consumer Defensive),Industry (Energy),Industry (Financial),
Industry (Healthcare),Industry (Industrials),Industry (Real Estate),Industry (Technology),
Industry (Utilities),Country (U.S. listed stocks only),Capitalization]
```

valuation of sectors, industry, country. [Source: Finviz]
* -g : Data group (sector, industry or country). Default: Sector.

<img width="1020" alt="sec_val" src="https://user-images.githubusercontent.com/25267873/113647490-d2b62780-9682-11eb-8346-089bd0499ba9.png">


## performance <a name="performance"></a>

```shell
usage: performance [-g Sector,Industry,Industry (Basic Materials),Industry (Communication Services),
Industry (Consumer Cyclical),Industry (Consumer Defensive),Industry (Energy),Industry (Financial),
Industry (Healthcare),Industry (Industrials),Industry (Real Estate),Industry (Technology),
Industry (Utilities),Country (U.S. listed stocks only),Capitalization]
```

performance of sectors, industry, country. [Source: Finviz]
* -g : Data group (sector, industry or country). Default: Sector.

<img width="1034" alt="ind_per" src="https://user-images.githubusercontent.com/25267873/113647513-dba6f900-9682-11eb-9b43-c1055af85536.png">


## spectrum <a name="spectrum"></a>

```
usage: spectrum [-g Sector,Industry,Industry (Basic Materials),Industry (Communication Services),
Industry (Consumer Cyclical),Industry (Consumer Defensive),Industry (Energy),Industry (Financial),
Industry (Healthcare),Industry (Industrials),Industry (Real Estate),Industry (Technology),
Industry (Utilities),Country (U.S. listed stocks only),Capitalization]
```

Spectrum of sectors, industry, country. [Source: Finviz]
* -g : Data group (sector, industry or country). Default: Sector.

![cntry_spec](https://user-images.githubusercontent.com/25267873/113639067-48fd5e80-9670-11eb-95cf-0931845ddd12.png)


## latest <a name="latest"></a>

```
usage: latest [-i N_ID] [-n N_NUM] [-d DATE]
```

Latest news articles. [Source: Seeking Alpha]
* -i : Article ID number.
* -n : Number of articles being printed. Default 10.
* -d : Date of news article.

<img width="1208" alt="latest" src="https://user-images.githubusercontent.com/25267873/115089633-926c6a00-9f0a-11eb-9d0e-1eedfd8ba7ce.png">


## trending <a name="trending"></a>

```
usage: trending [-i N_ID] [-n N_NUM]
```

Trending news articles. [Source: Seeking Alpha]
* -i : Article ID number.
* -n : Number of articles being printed. Default 10.

<img width="1213" alt="trending" src="https://user-images.githubusercontent.com/25267873/115089640-96988780-9f0a-11eb-9ca7-70a245fa3960.png">


## ratings <a name="ratings"></a>

```
usage: ratings [-t N_THRESHOLD]
```

Top ratings updates. [Source: MarketBeat]

* -t : Minimum threshold in percentage change between current and target price to show ratings. Default: 100.

<img width="963" alt="ratings" src="https://user-images.githubusercontent.com/25267873/115095983-4544c400-9f1b-11eb-8869-8ec8a0f8eae0.png">


## darkpool <a name="darkpool"></a>

```
usage: darkpool [-n N_NUM] [-t N_TOP]
```

Display dark pool (ATS) data of tickers with growing trades activity. [Source: FINRA]

* -n : Number of tickers to filter from entire ATS data based on the sum of the total weekly shares quantity. Default: 1000.
* -t : List of tickers from most promising with better linear regression slope. Default: 5.

![darkpool](https://user-images.githubusercontent.com/25267873/115323195-8d642080-a17f-11eb-9ef8-d456ce769ab7.png)

## darkshort <a name="darkshort"></a>

```
usage: darkshort [-n NUM] [-s {sv,sv_pct,nsv,nsv_dollar,dpp,dpp_dollar}]
```
Get dark pool short positions. [Source: Stockgrid]
* -n: Number of top tickers to show
* -s: Field for which to sort by, where 'sv': Short Vol. (1M), 'sv_pct': Short Vol. %, 'nsv': Net Short Vol. (1M), 'nsv_dollar': Net Short Vol. ($100M), 'dpp': DP Position (1M), 'dpp_dollar': DP Position ($1B). Default: dpp_dollar.
* --export: Save dataframe as a csv file. Default: false.

<img width="945" alt="darkshort" src="https://user-images.githubusercontent.com/25267873/122323732-76dc0a80-cf1f-11eb-9983-fd7688778016.png">


## shortvol <a name="darkpool"></a>

```
usage: shortvol [-n NUM] [-s {float,dtc,si}] [-h]
```

Print short interest and days to cover. [Source: Stockgrid]
* -n: Number of top tickers to show
* -s: Field for which to sort by, where 'float': Float Short %, 'dtc': Days to Cover, 'si': Short Interest. Default: float.
* -a: Data in ascending order. Default: false.
* --export: Save dataframe as a csv file. Default: false.

<img width="949" alt="shortvol" src="https://user-images.githubusercontent.com/25267873/122323861-af7be400-cf1f-11eb-9de2-5c7f2debddf0.png">

