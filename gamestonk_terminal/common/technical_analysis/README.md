# TECHNICAL ANALYSIS

This menu aims to perform a technical analysis on a pre-loaded ticker chart, and the usage of the following commands
along with an example will be exploited below.

* [view](#view)
  * view historical data and trendlines [Finviz]
* [summary](#summary)
  * technical summary report [FinBrain API]
* [recom](#recom)
  * recommendation based on Technical Indicators [Tradingview API]
* [pr](#pr)
  * pattern recognition [Finnhub]

[OVERLAP](#OVERLAP)

* [ema](#ema)
  * exponential moving average
* [sma](#sma)
  * simple moving average
* [vwap](#vwap)
  * volume weighted average price

[MOMENTUM](#MOMENTUM)

* [cci](#cci)
  * commodity channel index
* [macd](#macd)
  * moving average convergence/divergence
* [rsi](#rsi)
  * relative strength index
* [stoch](#stoch)
  * stochastic oscillator

[TREND](#TREND)

* [adx](#adx)
  * average directional movement index
* [aroon](#aroon)
  * aroon indicator

[VOLATILITY](#VOLATILITY)

* [bbands](#bbands)
  * bollinger bands

[VOLUME](#VOLUME)

* [ad](#ad)
  * Accumulation/distribution line values
* [obv](#obv)
  * on balance volume

[CUSTOM](#CUSTOM)

* [fib](#fib)
  * Shows fibonocci levels

**S/O to <https://github.com/twopirllc/pandas-ta>** _Owing to this library, it is fairly easy to add other technical
indicators. So, let us know if there's any other that you would like._

## view  <a name="view"></a>

```text
usage: view
```

View historical price with trendlines. [Source: Finviz]

![aapl](https://user-images.githubusercontent.com/25267873/113757843-02107700-970b-11eb-99ab-eb9b1312547f.png)

## summary  <a name="summary"></a>

```text
usage: summary
```

Technical summary report provided by FinBrain's API. FinBrain Technologies develops deep learning algorithms for
financial analysis and prediction, which currently serves traders from more than 150 countries all around the world.
[Source: <https://finbrain.tech>]

<img width="976" alt="Captura de ecrã 2021-03-29, às 00 31 29" src="https://user-images.githubusercontent.com/25267873/112772089-db758080-9026-11eb-93d5-9fd7a4b40380.png">

## recom  <a name="recom"></a>

```text
usage: recom [-s {crypto,forex,cfd}] [-e EXCHANGE] [-i {1M,1W,1d,4h,1h,15m,5m,1m}]
```

Print tradingview recommendation based on technical indicators. [Source: <https://pypi.org/project/tradingview-ta/>]

* -s : screener. Default america.
* -e : exchange, e.g. NASDAQ, NYSE. Default uses Alpha Vantage to get this information from ticker
* -i : interval. Default is showing all of different intervals.

<img width="977" alt="Recom" src="https://user-images.githubusercontent.com/25267873/113069531-76ea2b00-91b8-11eb-8934-9f693d3b4ffa.png">

## pr  <a name="pr"></a>

```text
usage: pr [-r {1,5,15,30,60,D,W,M}]
```

Display pattern recognition signals on the data. [Source: <https://finnhub.io>]

* -r : Plot resolution to look for pattern signals. Default 'D'.

![pr](https://user-images.githubusercontent.com/25267873/116812520-06338700-ab47-11eb-8db4-8f5e940507ed.png)

<img width="985" alt="PR" src="https://user-images.githubusercontent.com/25267873/116812505-f6b43e00-ab46-11eb-9776-fa469dc3d3f0.png">

# OVERLAP <a name="OVERLAP"></a>

## ema  <a name="ema"></a>

```text
usage: ema [-l N_LENGTH] [-o N_OFFSET]
```

![ema](https://user-images.githubusercontent.com/25267873/108602300-33bac200-7399-11eb-971a-f23f7097aba3.png)

## sma  <a name="sma"></a>

```text
usage: sma [-l L_LENGTH] [-o N_OFFSET]
```

![sma](https://user-images.githubusercontent.com/25267873/108602304-36b5b280-7399-11eb-86fe-d490fb32aaff.png)

## vwap  <a name="vwap"></a>

VWAP is available for intraday data.  This plots the most recent day only.

```text
usage: vwap [-o N_OFFSET]
```

![vwap](https://user-images.githubusercontent.com/18151143/127217340-0f38bafd-fc16-4be4-a80a-6b89913559f5.png)

# MOMENTUM <a name="MOMENTUM"></a>

## cci  <a name="cci"></a>

```text
usage: cci [-l N_LENGTH] [-s N_SCALAR] [-o N_OFFSET]
```

![cci](https://user-images.githubusercontent.com/25267873/108602745-96ad5880-739b-11eb-9e86-a1706c3ecb1f.png)

## macd  <a name="macd"></a>

```text
usage: macd [-f N_FAST] [-s N_SLOW] [--signal N_SIGNAL] [-o N_OFFSET]
```

![macd](https://user-images.githubusercontent.com/25267873/108602739-92813b00-739b-11eb-8a4e-8fa7ed66b2b6.png)

## rsi  <a name="rsi"></a>

```text
usage: rsi [-l N_LENGTH] [-s N_SCALAR] [-d N_DRIFT] [-o N_OFFSET]
```

![rsi](https://user-images.githubusercontent.com/25267873/108602743-957c2b80-739b-11eb-9d0d-6f530b3abb91.png)

## stoch  <a name="stoch"></a>

```text
usage: stoch [-k N_FASTKPERIOD] [-d N_SLOWDPERIOD] [--slowkperiod N_SLOWKPERIOD] [-o N_OFFSET]
```

![stoch](https://user-images.githubusercontent.com/25267873/108602744-9614c200-739b-11eb-8e4d-2cdc9981cb67.png)

# TREND <a name="TREND"></a>

## adx  <a name="adx"></a>

```text
usage: adx [-l N_LENGTH] [-s N_SCALAR] [-d N_DRIFT] [-o N_OFFSET]
```

![adx](https://user-images.githubusercontent.com/25267873/108602991-2bfd1c80-739d-11eb-973f-b836c1b839e6.png)

## aroon  <a name="aroon"></a>

```text
usage: aroon [-l N_LENGTH] [-s N_SCALAR] [-o N_OFFSET]
```

![aroon](https://user-images.githubusercontent.com/25267873/108602987-2b648600-739d-11eb-9a90-154145190595.png)

# VOLATILITY <a name="VOLATILITY"></a>

## bbands  <a name="bbands"></a>

```text
usage: bbands [-h] [-l N_LENGTH] [-s N_STD] [-m S_MAMODE] [-o N_OFFSET]
```

![bbands](https://user-images.githubusercontent.com/25267873/108602984-28699580-739d-11eb-9b82-2683a9840145.png)

# VOLUME <a name="VOLUME"></a>

## ad  <a name="ad"></a>

```text
usage: ad [-o N_OFFSET] [--open]
```

![ad](https://user-images.githubusercontent.com/18151143/127217265-73415705-3321-478f-b5a0-3ae1487c74ac.png)

## obv  <a name="obv"></a>

```text
usage: obv [-o N_OFFSET]
```

![obv](https://user-images.githubusercontent.com/18151143/127217286-d73c1079-1b84-4da9-a5d4-39f4eb2d6b1b.png)

# CUSTOM <a name="CUSTOM"></a>

## fib <a name="fib"></a>

Shows fibonocci levels

```python
usage: fib [-p PERIOD] [--start] [--end]
```

* -p/--period: Number of days to lookback for retracement.  Default = 120.
* --start: Allows for custom selection of min point.
* --end : Allows for custom selection of max point.

The fibonocci retracement works by looking at a minimum and maximum point.  Between these values, there is typically
support/resistance at 23.5 %, 38.2%, 50% and 61.8%.  Those values follow the golden ratio from the fibonocci sequence.

The `--start` and `--end` flags allow the user to select dates for the min and max points as your retracement levels.
Both flags are required if using.

![Fib1](https://user-images.githubusercontent.com/18151143/127217240-0b4cd88b-8fd3-484f-941e-b02a0efe08dd.png)
