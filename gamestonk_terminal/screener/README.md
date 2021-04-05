# SCREENER

This menu aims to filter stocks based on pre-specified preset filters, and the usage of the following commands along with an example will be exploited below.

* [view](#view)
  * view available presets
* [set](#set)
  * set one of the available presets
* [overview](#overview)
  * overview information [Finviz]
* [valuation](#valuation)
  * valuation information [Finviz]
* [financial](#financial)
  * financial information [Finviz]
* [ownership](#ownership)
  * ownership information [Finviz]
* [performance](#performance)
  * performance information [Finviz]
* [technical](#technical)
  * technical information [Finviz]
* [signals](#signals)
  * view filter signals (e.g. -s top_gainers) [Finviz]


## view <a name="view"></a>

```text
view
```

View available presets under presets folder.

<img width="938" alt="Captura de ecrã 2021-04-05, às 20 13 28" src="https://user-images.githubusercontent.com/25267873/113615237-856a9380-964b-11eb-9e39-a65f0291746d.png">


## set <a name="set"></a>

```text
usage: set [-p {template,sexy_year,...}]
```

Set preset from under presets folder.

* -p : Filter presets


## overview <a name="overview"></a>

```text
usage: overview [-p {template,sexy_year,...}] [-s {top_gainers,top_losers,...}] [-l LIMIT] [-a] 
```

Prints screener data of the companies that meet the pre-set filtering. The fields shown correspond to the type of function called, i.e.: overview, valuation, financial,
ownership, performance, technical. Note that when the signal parameter (-s) is specified, the preset is disregarded. [Source: Finviz]

* -p : Filter presets. Default: one pre-loaded in screener menu.
* -s : Signal type. Defaul: None. When specified (see list available in [signals](#signals)), the preset is disregarded.
* -l : Limit of stocks to output. Default: 200.
* -a : Set order of stocks shown to Ascended. Default: Descended.


## valuation <a name="valuation"></a>

```text
usage: valuation [-p {template,sexy_year,...}] [-s {top_gainers,top_losers,...}] [-l LIMIT] [-a] 
```

Prints screener data of the companies that meet the pre-set filtering. The fields shown correspond to the type of function called, i.e.: overview, valuation, financial,
ownership, performance, technical. Note that when the signal parameter (-s) is specified, the preset is disregarded. [Source: Finviz]

* -p : Filter presets. Default: one pre-loaded in screener menu.
* -s : Signal type. Defaul: None. When specified (see list available in [signals](#signals)), the preset is disregarded.
* -l : Limit of stocks to output. Default: 200.
* -a : Set order of stocks shown to Ascended. Default: Descended.


## financial <a name="financial"></a>

```text
usage: financial [-p {template,sexy_year,...}] [-s {top_gainers,top_losers,...}] [-l LIMIT] [-a] 
```

Prints screener data of the companies that meet the pre-set filtering. The fields shown correspond to the type of function called, i.e.: overview, valuation, financial,
ownership, performance, technical. Note that when the signal parameter (-s) is specified, the preset is disregarded. [Source: Finviz]

* -p : Filter presets. Default: one pre-loaded in screener menu.
* -s : Signal type. Defaul: None. When specified (see list available in [signals](#signals)), the preset is disregarded.
* -l : Limit of stocks to output. Default: 200.
* -a : Set order of stocks shown to Ascended. Default: Descended.


## ownership <a name="ownership"></a>

```text
usage: ownership [-p {template,sexy_year,...}] [-s {top_gainers,top_losers,...}] [-l LIMIT] [-a] 
```

Prints screener data of the companies that meet the pre-set filtering. The fields shown correspond to the type of function called, i.e.: overview, valuation, financial,
ownership, performance, technical. Note that when the signal parameter (-s) is specified, the preset is disregarded. [Source: Finviz]

* -p : Filter presets. Default: one pre-loaded in screener menu.
* -s : Signal type. Defaul: None. When specified (see list available in [signals](#signals)), the preset is disregarded.
* -l : Limit of stocks to output. Default: 200.
* -a : Set order of stocks shown to Ascended. Default: Descended.


## technical <a name="technical"></a>

```text
usage: technical [-p {template,sexy_year,...}] [-s {top_gainers,top_losers,...}] [-l LIMIT] [-a] 
```

Prints screener data of the companies that meet the pre-set filtering. The fields shown correspond to the type of function called, i.e.: overview, valuation, financial,
ownership, performance, technical. Note that when the signal parameter (-s) is specified, the preset is disregarded. [Source: Finviz]

* -p : Filter presets. Default: one pre-loaded in screener menu.
* -s : Signal type. Defaul: None. When specified (see list available in [signals](#signals)), the preset is disregarded.
* -l : Limit of stocks to output. Default: 200.
* -a : Set order of stocks shown to Ascended. Default: Descended.


## signals <a name="signals"></a>

```text
usage: signals
```

Prints list of available signals. [Source: Finviz]

<img width="937" alt="Captura de ecrã 2021-04-05, às 20 25 13" src="https://user-images.githubusercontent.com/25267873/113616495-0ece9580-964d-11eb-97af-4150f928a170.png">




