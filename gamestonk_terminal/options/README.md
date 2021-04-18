# OPTIONS DATA

This menu aims to give insight on options. options can cause significant share price movement, and option pricing gives
info about market sentiment for a ticker.

* [volume](#volume)
  * Show traded options for a given expiry [Yahoo Finance]

* [chains](#chains)
  * Display option chains for 

## volume <a name="get"></a>

```text
usage: volume -e yyyy-mm-dd 
```

or

```text
usage: volume --expiry yyyy-mm-dd 
```


Display volume graph for a date. [Source: Yahoo Finance]

* -e, --expiry : expiration date.

## chains <a name="chains"></a>
Display a table of options chains.

This data requires a Tradier sandbox developer account, which can be made [here](#https://tradier.com/products/market-data-api)

````
usage: chains [--calls] [--puts] [-m MIN] [-M MAX]
````
* --calls  : Flag to only display call options
* --puts   : Flag to display only put options
* -m       : Minimum strike price to show
* -M       : Maximum strike price to show

For combines tables, call options are on the left and put options are on the right of the strike

As an example, if I load my ticker and select an expiry, to view the options chain for strikes between $129 and $135, one would use:

````
chains -m 129 -M 135
````
Which outputs:
![im](https://user-images.githubusercontent.com/18151143/115068041-b191da00-9ebf-11eb-941e-4e255787ab94.png)
