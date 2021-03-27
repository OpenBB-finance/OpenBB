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

<img width="983" alt="summary" src="https://user-images.githubusercontent.com/25267873/112729900-6cb0fe00-8f26-11eb-8a6b-0dda0a9113d9.png">


## hist <a name="hist"></a>

```text
usage: hist
```

Plot histogram and density

![hist](https://user-images.githubusercontent.com/25267873/112729911-75a1cf80-8f26-11eb-925c-252a90657128.png)


## cdf <a name="cdf"></a>

```text
usage: cdf
```

Plot cumulative distribution function

![cdf](https://user-images.githubusercontent.com/25267873/112729910-75a1cf80-8f26-11eb-801a-2b44b193022b.png)


## bwy <a name="bwy"></a>

```text
usage: bwy
```

Box and Whisker plot yearly

![bwy](https://user-images.githubusercontent.com/25267873/112729912-763a6600-8f26-11eb-81b6-3df0b632b3af.png)


## bwm <a name="bwm"></a>

```text
usage: bwm
```

Box and Whisker plot monthly

![bwm](https://user-images.githubusercontent.com/25267873/112729913-76d2fc80-8f26-11eb-8338-448147ed5703.png)


## rolling <a name="rolling"></a>

```text
usage: rolling [-w ROLLING_WINDOW]
```

Rolling mean and std deviation

* -w : rolling window. Default 100.

![rolling](https://user-images.githubusercontent.com/25267873/112729908-75093900-8f26-11eb-9056-16bac2f54386.png)


## decompose <a name="decompose"></a>

```text
usage: decompose [-m]
```

Decompose time series as:
 - Additive Time Series = Level + CyclicTrend + Residual + Seasonality
 - Multiplicative Time Series = Level * CyclicTrend * Residual * Seasonality

* -m : multiplicative model. Default additive.

![decompose](https://user-images.githubusercontent.com/25267873/112729282-4c337480-8f23-11eb-913c-f30e5c0ef459.png)

<img width="972" alt="Captura de ecrã 2021-03-27, às 17 32 05" src="https://user-images.githubusercontent.com/25267873/112729352-9157a680-8f23-11eb-9db7-6ecc760a4a25.png">


## cusum <a name="cusum"></a>

```text
usage: cusum [-t THRESHOLD] [-d DRIFT]
```

Cumulative sum algorithm (CUSUM) to detect abrupt changes in data

* -t : threshold. Default (MAX-min)/40.
* -d : drift. Default (MAX-min)/80.

![cusum](https://user-images.githubusercontent.com/25267873/112729206-ef37be80-8f22-11eb-9a53-8e8e55c4caf0.png)

