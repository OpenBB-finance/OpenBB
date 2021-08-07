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
* [unu](#unu)
  * Display unusual options activity
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
* [grhist](#grhist)
   * Plot historical option greek [Source: ops.syncretism.io]



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

![calc](https://user-images.githubusercontent.com/18151143/126883982-c54cb5ec-7eb2-41c1-812e-75e830e3703d.png)

## unu <a name="unu"></a>
Show unusual options activity from fdscreener.com

```python
usage: unu [-n NUM] [--sortby] [-a] [--export] [-h]
```
* -n/--num : Number to get.  Defaults to 20.  Each page scrapes 20 results
* --sortby : Column to sort data by.  Can be {Option,Vol/OI,Vol,OI,Bid,Ask}.  Defaults to Vol/OI
* -a : Flag to sort in ascending order
* --export : Flag to export.  Can be {csv, json, xlsx}
```python
(✨) (op)> unu -n 5
Last Updated: 2021-08-03 18:06:07
╒══════════╤════════════╤══════════╤══════════╤═══════╤══════╤═══════╤═══════╕
│ Ticker   │ Exp        │ Option   │   Vol/OI │   Vol │   OI │   Bid │   Ask │
╞══════════╪════════════╪══════════╪══════════╪═══════╪══════╪═══════╪═══════╡
│ AMD      │ 2021-08-06 │ 112.0 P  │    102.9 │ 15639 │  152 │  1.67 │  1.69 │
├──────────┼────────────┼──────────┼──────────┼───────┼──────┼───────┼───────┤
│ MA       │ 2021-11-19 │ 375.0 C  │     50.3 │ 10165 │  202 │ 18.35 │ 18.65 │
├──────────┼────────────┼──────────┼──────────┼───────┼──────┼───────┼───────┤
│ GOOG     │ 2021-08-06 │ 2630.0 P │     38.5 │  5314 │  138 │  1.2  │  1.65 │
├──────────┼────────────┼──────────┼──────────┼───────┼──────┼───────┼───────┤
│ AMD      │ 2021-08-06 │ 111.0 P  │     37.2 │ 15245 │  410 │  1.29 │  1.31 │
├──────────┼────────────┼──────────┼──────────┼───────┼──────┼───────┼───────┤
│ GOOG     │ 2021-08-06 │ 2635.0 P │     34.1 │  5966 │  175 │  1.4  │  1.8  │
╘══════════╧════════════╧══════════╧══════════╧═══════╧══════╧═══════╧═══════╛
```

## exp <a name="exp"></a>
See/set expiry dates.
```text
usage: exp [-d] [-D
```

* -d : Expiry date index to set.
* -D : Date to set

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
To set 2021-08-13, the following two options are equivalent
```python
exp 2
exp -D 2021-08-13
```
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

![chains](https://user-images.githubusercontent.com/18151143/126855845-4f156b6d-a368-4e66-8dc9-b971792128d8.png)

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

![oi](https://user-images.githubusercontent.com/18151143/126855897-87eadd56-cca0-4eb0-8e55-6b7035762cbc.png)

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
![vol](https://user-images.githubusercontent.com/18151143/126855840-8fc3446d-081e-4961-9925-eb6c6e51c136.png)

## voi <a name="voi"></a>

```text
usage: voi [-v MIN_VOL] [-m MIN_SP] [-M MAX_SP] [--source]
```

Plots Volume + Open Interest of calls vs puts.

* -v : Minimum volume (considering open interest) threshold of the plot.
* -m : Minimum strike price to consider in the plot.
* -M : Maximum strike price to consider in the plot.
* --source: Data source.  Can be ['yf','tr'].  Defaults to 'tr' for Tradier.

![voi](https://user-images.githubusercontent.com/18151143/126855842-927ca7ff-78ca-46ce-9cc0-2a8dff4593af.png)

## hist <a name="hist"></a>
Shows historical option chain
```python
usage: hist [-s STRIKE] [--put] [--chain CHAIN_ID] [--raw] [--export {csv,json,xlsx}] [-h]
```
* -s/--strike: Strike to show history for
* --put: Flag to indicate the option is a put
* --chain: OCC Chain ID.  Example: AAPL210730C00144000.  This flag overwrites the strike and put option
* --raw: Show raw output
* --export: Export file.  Can be {csv, json, xlsx}.

Note that the chain ID can be obtained by using `chains -d symbol`

![hist](https://user-images.githubusercontent.com/18151143/126855841-6884b19b-63c8-4746-a63f-82ad1a523c0c.png)


## grhist <a name="grhist"></a>
Plot historical option greeks.  Data from ops.syncretism.io

```python
usage: grhist [-s STRIKE] [--put] [-g {iv,gamma,theta,vega,delta,rho,premium}] [--chain CHAIN_ID] [--raw] [--export {csv,json,xlsx}] [-h]
```
* -s/--strike: Strike to show history for
* -g/--greek: Greek to get data for.  Can be {iv,gamma,theta,vega,delta,rho}.  Also can be premium
* --put: Flag to indicate the option is a put
* --chain: OCC Chain ID.  Example: AAPL210730C00144000.  This flag overwrites the strike and put option
* --raw: Show raw output (last 20 entries)
* --export: Export file.  Can be {csv, json, xlsx}.

```python
(✨) (op)> grhist -s 145 --put -g delta
```
![gr_hist](https://user-images.githubusercontent.com/18151143/126881002-c516d94b-5c87-43b1-9e16-dce304795e1c.png)
