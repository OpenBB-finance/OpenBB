# RESIDUAL ANALYSIS

This menu aims to perform residual analysis on a pre-loaded stock in order to do statistical modeling, and the usage of the following commands along with an example will be exploited below.

* [pick](#pick)
  * pick one of the model fitting
* [fit](#fit)
  * show model fit against stock
* [res](#res)
  * show residuals
* [hist](#hist)
  * histogram and density curve
* [qqplot](#qqplot)
  * residuals against standard normal curve
* [acf](#acf)
  * (partial) auto-correlation function
* [normality](#normality)
  * normality test (Kurtosis,Skewness,...)
* [goodness](#goodness)
  * goodness of fit test (Kolmogorov-Smirnov)
* [arch](#arch)
  * autoregressive conditional heteroscedasticity
* [unitroot](#unitroot)
  * unit root test / stationarity (ADF, KPSS)
* [independence](#independence)
  * tests independent and identically distributed (BDS)

## pick <a name="pick"></a>

```text
usage: pick [-m MODEL]
```

Pick model to fit to stock data

* -m : model to fit to stock data. Default: None.


## fit <a name="fit"></a>

```text
usage: fit
```

Plot model fitting


## res <a name="res"></a>

```text
usage: res
```

Plot residuals


## hist <a name="hist"></a>

```text
usage: hist
```

Histogram and density curve



## qqplot <a name="qqplot"></a>

```text
usage: qqplot
```

Qqplot time series against a standard normal curve


## acf <a name="acf"></a>

```text
usage: acf [-l LAGS]
```

(partial) auto-correlation function

* -l : maximum lags to display in plots. Default 40.


## normality <a name="normality"></a>

```text
usage: normality
```

normality test (Kurtosis,Skewness,...)


## goodness <a name="goodness"></a>

```text
usage: goodness
```

goodness of fit test (Kolmogorov-Smirnov)


## arch <a name="arch"></a>

```text
usage: arch
```

autoregressive conditional heteroscedasticity with Engle's test


## unitroot <a name="unitroot"></a>

```text
usage: unitroot
```

unit root test / stationarity (ADF, KPSS)


## independence <a name="independence"></a>

```text
usage: independence
```

tests independent and identically distributed (i.i.d.) time series (BDS)
