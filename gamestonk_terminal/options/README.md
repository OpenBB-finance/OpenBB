# OPTIONS

This menu aims to give insight on options.

This menu aims to give insight on options. Options can cause significant share price movement, and option pricing gives info about market sentiment for a ticker. The usage of the following commands along with an example will be exploited below:

* [disp](#disp)
  * Display all preset screeners filters
* [scr](#scr)
  * Output screener options
* [load](#load)
  * Load new ticker
* [info](#info)
  * Display option information [Source: Barchart.com]
* [calc](#calc)
  * basic call/put PnL calculator
* [exp](#exp)
  * See/set expiry date
* [chains](#chains)
  * Display option chains with greeks [Source: Tradier.com]
* [oi](#oi)
  * Plot open interest
* [vol](#vol)
  * Plot volume
* [voi](#voi)
  * Plot volume and open interest
* [hist](#hist)
  * Plot option history [Source: Tradier.com]



## disp <a name="disp"></a>

```text
usage: view [-p {template,...}]
```

View available presets under [presets folder](/gamestonk_terminal/options/presets/).

* -p : View specific preset

<img width="979" alt="Captura de ecrã 2021-06-27, às 02 32 21" src="https://user-images.githubusercontent.com/25267873/123530365-59fac080-d6f1-11eb-85e1-536f7e927308.png">

## scr <a name="scr"></a>

```text
usage: scr [-p {template,...}]
```

Sreener filter output from https://ops.syncretism.io/index.html. Where: CS: Contract Symbol; S: Symbol, T: Option Type; Str: Strike; Exp v: Expiration; IV:
Implied Volatility; LP: Last Price; B: Bid; A: Ask; V: Volume; OI: Open Interest; Y: Yield; MY: Monthly Yield; SMP: Regular Market Price; SMDL: Regular Market
Day Low; SMDH: Regular Market Day High; LU: Last Trade Date; LC: Last Crawl; ITM: In The Money; PC: Price Change; PB: Price-to-book. [Source: Ops.Syncretism]

* -p : Filter presets

<img width="1220" alt="Captura de ecrã 2021-06-27, às 02 31 28" src="https://user-images.githubusercontent.com/25267873/123530368-5e26de00-d6f1-11eb-9a23-0b481b5efae1.png">

## load <a name="load"></a>
Load new ticker
```python
usage: load [-t Ticker]
```
* -t/--ticker: Ticker to load.  Flag is optional, as `load aapl` will also work

## info <a name="info"></a>
This scrapes the options information from barchart.com/stocks overview.  This includes information such as Historical Volatility and IV Rank.

````
usage: info
````

<img width="989" alt="opinfo" src="https://user-images.githubusercontent.com/25267873/115787028-80cb0c80-a3b9-11eb-97a4-ca208aed3be8.png">

## calc <a name="calc"></a>
Basic profit calculator for options
```python
usage: calc [-s STRIKE] [-p PREMIUM] [--put] [--sell]  [-h]
```
* -s/--strike : Strike price to consider
* -p/--premium: Premium being paid
* --put: Flag to calculate for put option
* --sell: Flag to calculate for selling option


## exp <a name="exp"></a>
See/set expiry dates.
```text
usage: exp [-d]
```

* -d : Expiry date index to set.

Running `exp` will show available option expirations
```python
(✨) (op)> exp

Available expiry dates:
    0.  2021-07-30
    1.  2021-08-06
    2.  2021-08-13
    3.  2021-08-20
    4.  2021-08-27
    5.  2021-09-03
```
So `exp 2` will set the expiration to '2021-08-13'

## chains <a name="chains"></a>

````
usage: chains [--calls] [--puts] [-m MIN_SP] [-M MAX_SP] [-d] [--export]
````

Display options chains. [Source: Tradier]

* --calls : Flag to show calls only
* --puts : Flag to show puts only
* -m : Minimum strike price to consider.
* -M : Maximum strike price to consider.
* -d : Columns to display.  Should be comma separated.  Must be in * -d : Columns to display from the following selection: symbol, bid, ask, strike, bidsize, asksize, volume, open_interest, delta, gamma, theta, vega, iv. Note that they are separated by comma.
* --export: Flag to export.  Options are {csv,json,xlsx}.

<img width="948" alt="chains" src="https://user-images.githubusercontent.com/25267873/115161876-f708ff80-a097-11eb-8073-195979862a45.png">

## oi <a name="oi"></a>
Plot open interest.
```python
usage: oi [-m MIN] [-M MAX] [--calls] [--puts] [--source {tr,yf}] [-h]
```
* -m/--min: Min strike to plot.  Defaults to .75 * current price
* -M/--max: Max strike to plot.  Defaults to 1.25 * current price
* --calls: Flag to plot calls only
* --puts: Flag to plot puts only
* --source: Data source.  Can be ['yf','tr'].  Defaults to 'tr' for Tradier.


## vol <a name="vol"></a>
Plot volume.
```python
usage: vol [-m MIN] [-M MAX] [--calls] [--puts] [--source {tr,yf}] [-h]
```
* -m/--min: Min strike to plot.  Defaults to .75 * current price
* -M/--max: Max strike to plot.  Defaults to 1.25 * current price
* --calls: Flag to plot calls only
* --puts: Flag to plot puts only
* --source: Data source.  Can be ['yf','tr'].  Defaults to 'tr' for Tradier.

## voi <a name="voi"></a>

```text
usage: voi [-v MIN_VOL] [-m MIN_SP] [-M MAX_SP] [--source]
```

Plots Volume + Open Interest of calls vs puts.

* -v : Minimum volume (considering open interest) threshold of the plot.
* -m : Minimum strike price to consider in the plot.
* -M : Maximum strike price to consider in the plot.
* --source: Data source.  Can be ['yf','tr'].  Defaults to 'tr' for Tradier.

![voinio](https://user-images.githubusercontent.com/25267873/115161878-f7a19600-a097-11eb-889b-e9cc945f174d.png)
