# EXPLORATORY DATA ANALYSIS

This menu aims to perform exploratory data analysis on a pre-loaded stock, and the usage of the following commands along with an example will be exploited below.

* [summary](#summary)
  * brief summary statistics
* [hist](#hist)
  * histogram with density plot
* [cdf](#cdf)
  * cumulative distribution function
* [bwy](#bwy)
  * box and whisker yearly plot
* [bwm](#bwm)
  * box and whisker monthly plot
* [rolling](#rolling)
  * rolling mean and std deviation
* [decompose](#decompose)
  * decomposition in cyclic-trend, season, and residuald
* [cusum](#cusum)
  * detects abrupt changes using cumulative sum algorithm


## summary <a name="summary"></a>

```text
usage: summary
```

Summary statistics



## hist <a name="hist"></a>

```text
usage: hist
```

Plot histogram and density



## cdf <a name="cdf"></a>

```text
usage: cdf
```

Plot cumulative distribution function



## bwy <a name="bwy"></a>

```text
usage: bwy
```

Box and Whisker plot yearly

![bwy](https://user-images.githubusercontent.com/25267873/112729437-ff03d280-8f23-11eb-87fb-a331747357f5.png)


## bwm <a name="bwm"></a>

```text
usage: bwm
```

Box and Whisker plot monthly

![bwm](https://user-images.githubusercontent.com/25267873/112729439-ff9c6900-8f23-11eb-9a63-8d60f23f1435.png)


## rolling <a name="rolling"></a>

```text
usage: rolling [-w ROLLING_WINDOW]
```

Rolling mean and std deviation

* -w : rolling window. Default 100.

![rolling](https://user-images.githubusercontent.com/25267873/112729342-843ab780-8f23-11eb-93f2-11c7c516d224.png)

<img width="972" alt="Captura de ecrã 2021-03-27, às 17 32 05" src="https://user-images.githubusercontent.com/25267873/112729352-9157a680-8f23-11eb-9db7-6ecc760a4a25.png">


## decompose <a name="decompose"></a>

```text
usage: decompose [-m]
```

Decompose time series as:
 - Additive Time Series = Level + CyclicTrend + Residual + Seasonality
 - Multiplicative Time Series = Level * CyclicTrend * Residual * Seasonality

* -m : multiplicative model. Default additive.

![decompose](https://user-images.githubusercontent.com/25267873/112729282-4c337480-8f23-11eb-913c-f30e5c0ef459.png)


## cusum <a name="cusum"></a>

```text
usage: cusum [-t THRESHOLD] [-d DRIFT]
```

Cumulative sum algorithm (CUSUM) to detect abrupt changes in data

* -t : threshold. Default (MAX-min)/40.
* -d : drift. Default (MAX-min)/80.

![cusum](https://user-images.githubusercontent.com/25267873/112729206-ef37be80-8f22-11eb-9a53-8e8e55c4caf0.png)

