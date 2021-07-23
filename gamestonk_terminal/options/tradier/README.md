# Tradier
This menu interfaces with the tradier sandbox api: https://developer.tradier.com

* [load](#load)
  * Load a ticker for looking up options
* [exp](#exp)
  * View all expiration dates and set which one.

* [oi](#oi)
  * Plots open interest

* [vol](#vol)
  * Plots volume

* [voi](#voi)
  * Plots open interest and volume



## load <a name="load"></a>
Loads a ticker
```python
usage: load [-t --ticker]
```
* -t/--ticker: Ticker to load.  Optional.  Using `load aapl` will load as well.

## exp <a name="exp"></a>

Shows all expiration and allows one to be set.
```python
usage: exp [-d]
```
* -d : Expiry date index to set

Running `exp` will return a list of available dates:
```python
(✨) (op)>(yf)> exp

Available expiry dates:
    0.  2021-07-23
    1.  2021-07-30
    2.  2021-08-06
    3.  2021-08-13
    4.  2021-08-20
    5.  2021-08-27
    6.  2021-09-03
```
So to select 2021-08-06, run `exp 2`

## oi <a name="oi"></a>
Plots open interest.  Open interest represents the number of contracts that exist.

```python
usage: oi [-m MIN] [-M MAX] [--calls] [--puts] [-h]
```
* -m/--min: Min strike to plot (defaults to 0.75 * current price)
* -M/--max: Max strike to plot (defaults to 1.25 * current price)
* --calls: Flag to show calls only
* --puts: Flag to show puts only

## vol <a name="vol"></a>
Plot volume. Volume refers to the number of contracts traded today.
```python
usage: vol [-m MIN] [-M MAX] [--calls] [--puts] [-h]
```
* -m/--min: Min strike to plot (defaults to 0.75 * current price)
* -M/--max: Max strike to plot (defaults to 1.25 * current price)
* --calls: Flag to show calls only
* --puts: Flag to show puts only
