# RESIDUAL ANALYSIS

This menu aims to perform residual analysis on a pre-loaded stock in order to do statistical modeling, and the usage of the following commands along with an example will be exploited below.

* [pick](#pick)
  * pick one of the model fitting
  * Currently Supported: **Naive**, **ARIMA**
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

Pick model to fit to stock data.
Currently supported: **Naive**, **ARIMA**


* -m : model to fit to stock data. Default: None.


## fit <a name="fit"></a>

```text
usage: fit
```

Plot model fitting

![fit](https://user-images.githubusercontent.com/25267873/112752708-362dbe80-8fcc-11eb-9321-1f5880bbba43.png)

## res <a name="res"></a>

```text
usage: res
```

Plot residuals

![res](https://user-images.githubusercontent.com/25267873/112752705-35952800-8fcc-11eb-8b0b-ec91ee54c019.png)


## hist <a name="hist"></a>

```text
usage: hist
```

Histogram and density curve

![hist](https://user-images.githubusercontent.com/25267873/112752704-35952800-8fcc-11eb-8b95-6d4cf1a1513b.png)

## qqplot <a name="qqplot"></a>

```text
usage: qqplot
```

Qqplot time series against a standard normal curve

![qqplot](https://user-images.githubusercontent.com/25267873/112752703-34fc9180-8fcc-11eb-93a0-7bf0c684ccd2.png)

## acf <a name="acf"></a>

```text
usage: acf [-l LAGS]
```

(partial) auto-correlation function

* -l : maximum lags to display in plots. Default 40.

![acf](https://user-images.githubusercontent.com/25267873/112752699-3463fb00-8fcc-11eb-976d-88a99cd6efcd.png)


## normality <a name="normality"></a>

```text
usage: normality
```

normality test (Kurtosis,Skewness,...)

<img width="972" alt="normality" src="https://user-images.githubusercontent.com/25267873/112752697-3332ce00-8fcc-11eb-8b74-257284e75d3c.png">


## goodness <a name="goodness"></a>

```text
usage: goodness
```

goodness of fit test (Kolmogorov-Smirnov)

<img width="966" alt="goodness" src="https://user-images.githubusercontent.com/25267873/112752696-329a3780-8fcc-11eb-8ce9-d639923880a5.png">


## arch <a name="arch"></a>

```text
usage: arch
```

autoregressive conditional heteroscedasticity with Engle's test

<img width="965" alt="arch" src="https://user-images.githubusercontent.com/25267873/112752702-34fc9180-8fcc-11eb-8668-0363f1a2b6ff.png">

## unitroot <a name="unitroot"></a>

```text
usage: unitroot
```

unit root test / stationarity (ADF, KPSS)

<img width="982" alt="unitroot" src="https://user-images.githubusercontent.com/25267873/112752698-33cb6480-8fcc-11eb-9c4f-fd0a59a01a88.png">

## independence <a name="independence"></a>

```text
usage: independence
```

tests independent and identically distributed (i.i.d.) time series (BDS)

<img width="974" alt="independence" src="https://user-images.githubusercontent.com/25267873/112752695-3201a100-8fcc-11eb-9760-3fdb26bb1c16.png">
