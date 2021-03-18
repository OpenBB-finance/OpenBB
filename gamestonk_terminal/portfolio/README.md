#PORTFOLIO

This was developed to interface with Robinhood.  

Once this screen is accessed, the first command to be run is 
````
login
````
Which will use your robinhood login infomation, which should be stored as environment variables or in the config_terminal.py

Currently there are 2 options:
* [hold](#hold)
    * Look at current (stock only) holdings
* [hist](#hist)
    * Get and plot historical portfolio

## hold <a name="hold"></a>

Displays current holdings to the console:

````
usage: hold
````
There are no additional flags.  This just prints all current stonks, their last price, previous close, your equity and
the % change from previous close.

Example:
![hold](https://user-images.githubusercontent.com/18151143/111685384-3c6ab080-87fe-11eb-80ce-9b256c396bf2.png)
## hist <a name="hist"></a>
Display your RH portfolio based on provided interval and span.  Based on the API data availablility, plotted as a candlestick chart.
````
usage: hist [-s --span] [-i --interval]
````
* -s/--span : How long to look back.  Defaults to the day. Options:
    * [day, week, month, 3month, year, 5year, all]
* -i/--interval: Data resolution. Defaults to 10minute intervals. Options:
    * [5minute, 10minute, hour, day, week]
    
Example Default Output:
![hist](https://user-images.githubusercontent.com/18151143/111685390-3d9bdd80-87fe-11eb-90f9-7ca8b0c1e7f8.png)