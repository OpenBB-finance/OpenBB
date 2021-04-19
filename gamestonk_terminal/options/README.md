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
usage: chains [--calls] [--puts] [-m MIN] [-M MAX] [-d DISPLAY]
````
* --calls  : Flag to only display call options
* --puts   : Flag to display only put options
* -m       : Minimum strike price to show
* -M       : Maximum strike price to show
* -d       : Columns to display.  Should be comma separated.  Must be in `['bid', 'ask', 'strike', 'bidsize', 'asksize', 'volume', 'open_interest',
        'delta', 'gamma', 'theta', 'vega', 'ask_iv', 'bid_iv','mid_iv']`

For combined tables, call options are on the left and put options are on the right of the strike

As an example, if I load my ticker and select an expiry, to view the options chain for strikes between $129 and $135, one would use:

````
chains -m 129 -M 135
````
Which outputs:
![im](https://user-images.githubusercontent.com/18151143/115068041-b191da00-9ebf-11eb-941e-4e255787ab94.png)

To change what columns are displayed, one can use the `-d` flag.  To show the same as above, but only the ask, ask size 
delta and theta variables, we would do:
````
chains -m 129 -M 135 -d ask,ask_size,delta,theta
````
Which outputs 
![im2](https://user-images.githubusercontent.com/18151143/115276719-640cab80-a111-11eb-84a2-4dc6a1685946.png)