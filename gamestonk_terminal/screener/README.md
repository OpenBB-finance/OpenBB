# SCREENER

This menu aims to filter stocks based on pre-specified preset filters, and the usage of the following commands along with an example will be exploited below.

* [view](#view)
  * view available presets
* [set](#set)
  * set one of the available presets
* [historical](#historical)
  * view historical price [Yahoo Finance]
* [overview](#overview)
  * overview data (e.g. Sector, Industry, Market Cap, Volume) [Finviz]
* [valuation](#valuation)
  * valuation data (e.g. P/E, PEG, P/S, P/B, EPS this Y) [Finviz]
* [financial](#financial)
  * financial data (e.g. Dividend, ROA, ROE, ROI, Earnings) [Finviz]
* [ownership](#ownership)
  * ownership data (e.g. Float, Insider Own, Short Ratio) [Finviz]
* [performance](#performance)
  * performance data (e.g. Perf Week, Perf YTD, Volatility M) [Finviz]
* [technical](#technical)
  * technical data (e.g. Beta, SMA50, 52W Low, RSI, Change) [Finviz]
  * contains [Oversold (-s) signal example](#signal-oversold)
* [signals](#signals)
  * view filter signals (e.g. -s top_gainers) [Finviz]
* [> po](portfolio_optimization/README.md)
  * **portfolio optimization for last screened tickers**

## view <a name="view"></a>

```text
usage: view [-p {template,sexy_year,...}]
```
View available presets under [presets folder](/gamestonk_terminal/screener/presets/).

* -p : View specific preset filters.

<img width="1203" alt="Captura de ecrã 2021-05-06, às 20 46 41" src="https://user-images.githubusercontent.com/25267873/117356901-30b97300-aeac-11eb-91fe-ed6495db6614.png">



## set <a name="set"></a>

```text
usage: set [-p {template,sexy_year,...}]
```

Set preset from under [presets folder](/gamestonk_terminal/screener/presets/).

* -p : Filter presets


## historical <a name="historical"></a>

```text
usage: historical [-t {o,h,l,c,a}] [-s {top_gainers,top_losers,...}] [--start START]
```

View historical price of stocks. [Source: Yahoo Finance]

* -t : Type of candle: Default 'a' for adjusted close.
* -s : Signal type. Default: None. When specified (see list available in [signals](#signals)), the preset is disregarded.
* --start : Start time with format "%Y-%m-%d". Default 6 months earlier.

![screener_view](https://user-images.githubusercontent.com/25267873/113784557-8bd13c00-972d-11eb-9776-0e192bb83515.png)

![top_gainers](https://user-images.githubusercontent.com/25267873/113784834-f97d6800-972d-11eb-8112-6c80f4e2cf5e.png)


## overview <a name="overview"></a>

```text
usage: overview [-p {template,sexy_year,...}] [-s {top_gainers,top_losers,...}] [-l LIMIT] [-aem]
```

Prints screener data of the companies that meet the pre-set filtering. Some of the fields shown are: Sector, Industry, Market Cap, Volume. Note that when the signal parameter (-s) is specified, the preset is disregarded. [Source: Finviz]

* -p : Filter presets. Default: one pre-loaded in screener menu.
* -s : Signal type. Default: None. When specified (see list available in [signals](#signals)), the preset is disregarded.
* -l : Limit of stocks to output. Default: 200.
* -a : Set order of stocks shown to Ascended. Default: Descended.
* -e : Export list to a file.
* -m : Run papermill dd on the tickers in the returned list.

<img width="934" alt="overview" src="https://user-images.githubusercontent.com/25267873/113618972-4854d000-9650-11eb-9482-d1054a7d0451.png">


## valuation <a name="valuation"></a>

```text
usage: valuation [-p {template,sexy_year,...}] [-s {top_gainers,top_losers,...}] [-l LIMIT] [-aem]
```

Prints screener data of the companies that meet the pre-set filtering. Some of the fields shown are: P/E, PEG, P/S, P/B, EPS this Y. Note that when the signal parameter (-s) is specified, the preset is disregarded. [Source: Finviz]

* -p : Filter presets. Default: one pre-loaded in screener menu.
* -s : Signal type. Default: None. When specified (see list available in [signals](#signals)), the preset is disregarded.
* -l : Limit of stocks to output. Default: 200.
* -a : Set order of stocks shown to Ascended. Default: Descended.
* -e : Export list to a file.
* -m : Run papermill dd on the tickers in the returned list.

<img width="934" alt="overview" src="https://user-images.githubusercontent.com/25267873/113618972-4854d000-9650-11eb-9482-d1054a7d0451.png">


<img width="989" alt="valuation" src="https://user-images.githubusercontent.com/25267873/113618970-47bc3980-9650-11eb-8f3d-1b3609bb71ef.png">


## financial <a name="financial"></a>

```text
usage: financial [-p {template,sexy_year,...}] [-s {top_gainers,top_losers,...}] [-l LIMIT] [-aem]
```

Prints screener data of the companies that meet the pre-set filtering. Some of the fields shown are: Dividend, ROA, ROE, ROI, Earnings. Note that when the signal parameter (-s) is specified, the preset is disregarded. [Source: Finviz]

* -p : Filter presets. Default: one pre-loaded in screener menu.
* -s : Signal type. Default: None. When specified (see list available in [signals](#signals)), the preset is disregarded.
* -l : Limit of stocks to output. Default: 200.
* -a : Set order of stocks shown to Ascended. Default: Descended.
* -e : Export list to a file.
* -m : Run papermill dd on the tickers in the returned list.

<img width="934" alt="overview" src="https://user-images.githubusercontent.com/25267873/113618972-4854d000-9650-11eb-9482-d1054a7d0451.png">


<img width="995" alt="financial" src="https://user-images.githubusercontent.com/25267873/113618977-4985fd00-9650-11eb-976c-913232f5eb2f.png">


## ownership <a name="ownership"></a>

```text
usage: ownership [-p {template,sexy_year,...}] [-s {top_gainers,top_losers,...}] [-l LIMIT] [-aem]
```

Prints screener data of the companies that meet the pre-set filtering. Some of the fields shown are: Float, Insider Own, Short Ratio. Note that when the signal parameter (-s) is specified, the preset is disregarded. [Source: Finviz]

* -p : Filter presets. Default: one pre-loaded in screener menu.
* -s : Signal type. Default: None. When specified (see list available in [signals](#signals)), the preset is disregarded.
* -l : Limit of stocks to output. Default: 200.
* -a : Set order of stocks shown to Ascended. Default: Descended.
* -e : Export list to a file.
* -m : Run papermill dd on the tickers in the returned list.

<img width="934" alt="overview" src="https://user-images.githubusercontent.com/25267873/113618972-4854d000-9650-11eb-9482-d1054a7d0451.png">


<img width="1017" alt="ownership" src="https://user-images.githubusercontent.com/25267873/113618974-48ed6680-9650-11eb-99ec-fe584ebfa274.png">


## performance <a name="performance"></a>

```text
usage: performance [-p {template,sexy_year,...}] [-s {top_gainers,top_losers,...}] [-l LIMIT] [-aem]
```

Prints screener data of the companies that meet the pre-set filtering. Some of the fields shown are: Perf Week, Perf YTD, Volatility M. Note that when the signal parameter (-s) is specified, the preset is disregarded. [Source: Finviz]

* -p : Filter presets. Default: one pre-loaded in screener menu.
* -s : Signal type. Default: None. When specified (see list available in [signals](#signals)), the preset is disregarded.
* -l : Limit of stocks to output. Default: 200.
* -a : Set order of stocks shown to Ascended. Default: Descended.
* -e : Export list to a file.
* -m : Run papermill dd on the tickers in the returned list.

<img width="934" alt="overview" src="https://user-images.githubusercontent.com/25267873/113618972-4854d000-9650-11eb-9482-d1054a7d0451.png">


<img width="1016" alt="performance" src="https://user-images.githubusercontent.com/25267873/113618973-48ed6680-9650-11eb-8894-0c9ace262bfa.png">


## technical <a name="technical"></a>

```text
usage: technical [-p {template,sexy_year,...}] [-s {top_gainers,top_losers,...}] [-l LIMIT] [-aem]
```

Prints screener data of the companies that meet the pre-set filtering. Some of the fields shown are: Beta, SMA50, 52W Low, RSI, Change. Note that when the signal parameter (-s) is specified, the preset is disregarded. [Source: Finviz]

* -p : Filter presets. Default: one pre-loaded in screener menu.
* -s : Signal type. Default: None. When specified (see list available in [signals](#signals)), the preset is disregarded.
* -l : Limit of stocks to output. Default: 200.
* -a : Set order of stocks shown to Ascended. Default: Descended.
* -e : Export list to a file.
* -m : Run papermill dd on the tickers in the returned list.

<img width="934" alt="overview" src="https://user-images.githubusercontent.com/25267873/113618972-4854d000-9650-11eb-9482-d1054a7d0451.png">


<img width="749" alt="technical" src="https://user-images.githubusercontent.com/25267873/113619656-2b6ccc80-9651-11eb-92c2-87d7e51ef22d.png">


### signal oversold <a name="signal-oversold"></a>

Example:
```text
technical -s oversold [-em]
```

* -e : Export list to a file.
* -m : Run papermill dd on the tickers in the returned list.

<img width="934" alt="overview" src="https://user-images.githubusercontent.com/25267873/113618972-4854d000-9650-11eb-9482-d1054a7d0451.png">

<img width="1007" alt="technical_oversold flag" src="https://user-images.githubusercontent.com/25267873/113618975-48ed6680-9650-11eb-805f-00a656f97e9a.png">


## signals <a name="signals"></a>

```text
usage: signals
```

Prints list of available signals. [Source: Finviz]

<img width="937" alt="Captura de ecrã 2021-04-05, às 20 25 13" src="https://user-images.githubusercontent.com/25267873/113616495-0ece9580-964d-11eb-97af-4150f928a170.png">

## po <a name="port_opt"></a>
Goes to the portfolio menu with list of passed stocks. In order to pass the stocks, just type the tickers of interest, no commas.

```
usage: po ticker1 ticker2 ... 
```

````
example: po aapl msft tsla gme
````
