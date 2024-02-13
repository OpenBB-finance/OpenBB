---
title: garch
description: Calculates annualized volatility forecasts based on GARCH
keywords:
- econometrics
- garch
---

import HeadTitle from '@site/src/components/General/HeadTitle.tsx';

<HeadTitle title="econometrics /garch - Reference | OpenBB Terminal Docs" />

Calculates annualized volatility forecasts based on GARCH. GARCH (Generalized autoregressive conditional heteroskedasticity) is stochastic model for time series, which is for instance used to model volatility clusters, stock return and inflation. It is a generalisation of the ARCH models. $\text{GARCH}(p, q) = (1 - \alpha - \beta) \sigma_l + \sum_{i=1}^q \alpha u_{t-i}^2 + \sum_{i=1}^p \beta \sigma_{t-i}^2$ [1] The GARCH-model assumes that the variance estimate consists of 3 components: - $\sigma_l$ ; the long term component, which is unrelated to the current market conditions - $u_t$ ; the innovation/discovery through current market price changes - $\sigma_t$ ; the last estimate GARCH can be understood as a model, which allows to optimize these 3 variance components to the time series. This is done assigning weights to variance components: $(1 - \alpha - \beta)$ for $\sigma_l$ , $\alpha$ for $u_t$ and $\beta$ for $\sigma_t$ . [2] The weights can be estimated by iterating over different values of $(1 - \alpha - \beta) \sigma_l$ which we will call $\omega$ , $\alpha$ and $\beta$ , while maximizing: $\sum_{i} -ln(v_i) - (u_i ^ 2) / v_i$ . With the constraints: - $\alpha  0$ - $\beta  0$ - $\alpha + \beta  1$ Note that there is no restriction on $\omega$ . Another method used for estimation is "variance targeting", where one first sets $\omega$ equal to the variance of the time series. This method nearly as effective as the previously mentioned and is less computationally effective. One can measure the fit of the time series to the GARCH method by using the Ljung-Box statistic. [3] See the sources below for reference and for greater detail. Sources: [1] Generalized Autoregressive Conditional Heteroskedasticity, by Tim Bollerslev [2] Finance Compact Plus Band 1, by Yvonne Seler Zimmerman and Heinz Zimmerman; ISBN: 978-3-907291-31-1 [3] Options, Futures & other Derivates, by John C. Hull; ISBN: 0-13-022444-8

### Usage

```python wordwrap
garch -v {} [-p P] [-o O] [-q Q] [-m {LS,AR,ARX,HAR,HARX,constant,zero}] [-l HORIZON] [-d]
```

---

## Parameters

| Name | Parameter | Description | Default | Optional | Choices |
| ---- | --------- | ----------- | ------- | -------- | ------- |
| column | -v  --value | The column and name of the database you want to estimate volatility for | None | False | None |
| p | -p | The lag order of the symmetric innovation | 1 | True | None |
| o | -o | The lag order of the asymmetric innovation | 0 | True | None |
| q | -q | The lag order of lagged volatility or equivalent | 1 | True | None |
| mean | -m  --mean | Choose mean model | constant | True | LS, AR, ARX, HAR, HARX, constant, zero |
| horizon | -l  --length | The length of the estimate | 100 | True | None |
| detailed | -d  --detailed | Display the details about the parameter fit, for instance the confidence interval | False | True | None |

---
