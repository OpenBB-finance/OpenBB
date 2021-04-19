# OPTIONS

This menu aims to give insight on options. 

This menu aims to give insight on options. Options can cause significant share price movement, and option pricing gives info about market sentiment for a ticker. The usage of the following commands along with an example will be exploited below:

* [exp](#exp)
  * See/set expiry date [Yahoo Finance]
* [voi](#voi)
  * Volume + open interest options trading plot [Yahoo Finance]
* [vcalls](#vcalls)
  * Calls volume + open interest plot [Yahoo Finance]
* [vputs](#vputs)
  * Puts volume + open interest plot [Yahoo Finance]
* [chains](#chains)
  * Display option chains [Source: Tradier]


## exp <a name="exp"></a>

```text
usage: exp [-d {0,1,2,3,4,5,6,7,8,9,10,11}]
```

See/set expiry dates. [Source: Yahoo Finance]

* -d : Expiry date index to set.

<img width="955" alt="exp" src="https://user-images.githubusercontent.com/25267873/115161875-f6706900-a097-11eb-8566-bb7b408856a5.png">


## voi <a name="voi"></a>

```text
usage: voi [-v MIN_VOL] [-m MIN_SP] [-M MAX_SP]
```

Plots Volume + Open Interest of calls vs puts. [Source: Yahoo Finance]

* -v : Minimum volume (considering open interest) threshold of the plot.
* -m : Minimum strike price to consider in the plot.
* -M : Maximum strike price to consider in the plot.

![voinio](https://user-images.githubusercontent.com/25267873/115161878-f7a19600-a097-11eb-889b-e9cc945f174d.png)


## vcalls <a name="vcalls"></a>

```text
usage: vcalls [-m MIN_SP] [-M MAX_SP]
```

Plots Calls Volume + Open Interest. [Source: Yahoo Finance]

* -m : Minimum strike price to consider in the plot.
* -M : Maximum strike price to consider in the plot.

![vcalls](https://user-images.githubusercontent.com/25267873/115161874-f5d7d280-a097-11eb-93e2-3a2b20292f09.png)


## vputs <a name="vputs"></a>

```text
usage: vputs [-m MIN_SP] [-M MAX_SP]
```

Plots Puts Volume + Open Interest. [Source: Yahoo Finance]

* -m : Minimum strike price to consider in the plot.
* -M : Maximum strike price to consider in the plot.

![vputs](https://user-images.githubusercontent.com/25267873/115161873-f40e0f00-a097-11eb-8334-3d4f14b56766.png)


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
