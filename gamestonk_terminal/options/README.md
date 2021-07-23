# OPTIONS

This menu aims to give insight on options.

This menu aims to give insight on options. Options can cause significant share price movement, and option pricing gives info about market sentiment for a ticker. The usage of the following commands along with an example will be exploited below:

* [disp](#disp)
  * Display all preset screeners filters
* [scr](#scr)
  * Output screener options
* [info](#info)
  * Display option information [Source: Barchart.com]
* [calc](#calc)
  * Basic call/put PnL calculator

[yfinance option menu](/gamestonk_terminal/options/yfinance)

[tradier option menu](/gamestonk_terminal/options/tradier)



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

## calc <a name="calc"></a>
This provides an educational interface to visualize profit on options.
```python
usage: calc [-s STRIKE] [-p PREMIUM]  [--put] [--sell][-h]
```
* -s/--strike: Strike price of option
* -p/--premium: Premium being paid for option
* --put: Flag to indicate a put option
* --sell: Flag to indicate selling of an option

## info <a name="info"></a>
This scrapes the options information from barchart.com/stocks overview.  This includes information such as Historical Volatility and IV Rank.

````
usage: info
````

<img width="989" alt="opinfo" src="https://user-images.githubusercontent.com/25267873/115787028-80cb0c80-a3b9-11eb-97a4-ca208aed3be8.png">
