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
  * contains [Oversold (-s) signal example](#signal-oversold)
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

Prints screener data of the companies that meet the pre-set filtering. The fields shown correspond to the type of function called, i.e.: overview, valuation, financial, ownership, performance, technical. Note that when the signal parameter (-s) is specified, the preset is disregarded. [Source: Finviz]

* -p : Filter presets. Default: one pre-loaded in screener menu.
* -s : Signal type. Default: None. When specified (see list available in [signals](#signals)), the preset is disregarded.
* -l : Limit of stocks to output. Default: 200.
* -a : Set order of stocks shown to Ascended. Default: Descended.

<img width="934" alt="overview" src="https://user-images.githubusercontent.com/25267873/113618972-4854d000-9650-11eb-9482-d1054a7d0451.png">


## valuation <a name="valuation"></a>

```text
usage: valuation [-p {template,sexy_year,...}] [-s {top_gainers,top_losers,...}] [-l LIMIT] [-a] 
```

Prints screener data of the companies that meet the pre-set filtering. The fields shown correspond to the type of function called, i.e.: overview, valuation, financial, ownership, performance, technical. Note that when the signal parameter (-s) is specified, the preset is disregarded. [Source: Finviz]

* -p : Filter presets. Default: one pre-loaded in screener menu.
* -s : Signal type. Default: None. When specified (see list available in [signals](#signals)), the preset is disregarded.
* -l : Limit of stocks to output. Default: 200.
* -a : Set order of stocks shown to Ascended. Default: Descended.

<img width="989" alt="valuation" src="https://user-images.githubusercontent.com/25267873/113618970-47bc3980-9650-11eb-8f3d-1b3609bb71ef.png">


## financial <a name="financial"></a>

```text
usage: financial [-p {template,sexy_year,...}] [-s {top_gainers,top_losers,...}] [-l LIMIT] [-a] 
```

Prints screener data of the companies that meet the pre-set filtering. The fields shown correspond to the type of function called, i.e.: overview, valuation, financial, ownership, performance, technical. Note that when the signal parameter (-s) is specified, the preset is disregarded. [Source: Finviz]

* -p : Filter presets. Default: one pre-loaded in screener menu.
* -s : Signal type. Default: None. When specified (see list available in [signals](#signals)), the preset is disregarded.
* -l : Limit of stocks to output. Default: 200.
* -a : Set order of stocks shown to Ascended. Default: Descended.

<img width="995" alt="financial" src="https://user-images.githubusercontent.com/25267873/113618977-4985fd00-9650-11eb-976c-913232f5eb2f.png">


## ownership <a name="ownership"></a>

```text
usage: ownership [-p {template,sexy_year,...}] [-s {top_gainers,top_losers,...}] [-l LIMIT] [-a] 
```

Prints screener data of the companies that meet the pre-set filtering. The fields shown correspond to the type of function called, i.e.: overview, valuation, financial, ownership, performance, technical. Note that when the signal parameter (-s) is specified, the preset is disregarded. [Source: Finviz]

* -p : Filter presets. Default: one pre-loaded in screener menu.
* -s : Signal type. Default: None. When specified (see list available in [signals](#signals)), the preset is disregarded.
* -l : Limit of stocks to output. Default: 200.
* -a : Set order of stocks shown to Ascended. Default: Descended.

<img width="1017" alt="ownership" src="https://user-images.githubusercontent.com/25267873/113618974-48ed6680-9650-11eb-99ec-fe584ebfa274.png">


## performance <a name="performance"></a>

```text
usage: performance [-p {template,sexy_year,...}] [-s {top_gainers,top_losers,...}] [-l LIMIT] [-a] 
```

Prints screener data of the companies that meet the pre-set filtering. The fields shown correspond to the type of function called, i.e.: overview, valuation, financial, ownership, performance, technical. Note that when the signal parameter (-s) is specified, the preset is disregarded. [Source: Finviz]

* -p : Filter presets. Default: one pre-loaded in screener menu.
* -s : Signal type. Default: None. When specified (see list available in [signals](#signals)), the preset is disregarded.
* -l : Limit of stocks to output. Default: 200.
* -a : Set order of stocks shown to Ascended. Default: Descended.

<img width="1016" alt="performance" src="https://user-images.githubusercontent.com/25267873/113618973-48ed6680-9650-11eb-8894-0c9ace262bfa.png">


## technical <a name="technical"></a>

```text
usage: technical [-p {template,sexy_year,...}] [-s {top_gainers,top_losers,...}] [-l LIMIT] [-a] 
```

Prints screener data of the companies that meet the pre-set filtering. The fields shown correspond to the type of function called, i.e.: overview, valuation, financial,
ownership, performance, technical. Note that when the signal parameter (-s) is specified, the preset is disregarded. [Source: Finviz]

* -p : Filter presets. Default: one pre-loaded in screener menu.
* -s : Signal type. Default: None. When specified (see list available in [signals](#signals)), the preset is disregarded.
* -l : Limit of stocks to output. Default: 200.
* -a : Set order of stocks shown to Ascended. Default: Descended.

<img width="749" alt="technical" src="https://user-images.githubusercontent.com/25267873/113619656-2b6ccc80-9651-11eb-92c2-87d7e51ef22d.png">


### signal oversold <a name="signal-oversold"></a>

Example:
```text
technical -s oversold
```

<img width="1007" alt="technical_oversold flag" src="https://user-images.githubusercontent.com/25267873/113618975-48ed6680-9650-11eb-805f-00a656f97e9a.png">


## signals <a name="signals"></a>

```text
usage: signals
```

Prints list of available signals. [Source: Finviz]

<img width="937" alt="Captura de ecrã 2021-04-05, às 20 25 13" src="https://user-images.githubusercontent.com/25267873/113616495-0ece9580-964d-11eb-97af-4150f928a170.png">




