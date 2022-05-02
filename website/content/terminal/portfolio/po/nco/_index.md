```
usage: nco [-p HISTORIC_PERIOD] [-s START_PERIOD] [-e END_PERIOD] [-lr]
           [-f {d,w,m}] [-mn MAX_NAN] [-th THRESHOLD_VALUE]
           [-mt NAN_FILL_METHOD]
           [-cd {pearson,spearman,abs_pearson,abs_spearman,distance,mutual_info,tail}]
           [-cv {hist,ewma1,ewma2,ledoit,oas,shrunk,gl,jlogo,fixed,spectral,shrink}]
           [-o {MinRisk,Utility,Sharpe,ERC}]
           [-rm {MV,MAD,MSV,FLPM,SLPM,CVaR,EVaR,WR,ADD,UCI,CDaR,EDaR,MDD}]
           [-r RISK_FREE] [-ra RISK_AVERSION] [-a SIGNIFICANCE_LEVEL]
           [-lk {single,complete,average,weighted,centroid,median,ward,dbht}]
           [-k AMOUNT_CLUSTERS] [-mk MAX_CLUSTERS] [-bi AMOUNT_BINS]
           [-at ALPHA_TAIL] [-lo] [-de SMOOTHING_FACTOR_EWMA]
           [-v LONG_ALLOCATION] [--name NAME] [-h]
```

Convex optimization solutions tend to be unstable, to the point of entirely offsetting the benefits of optimization. For example, in the context of financial applications, it is known that portfolios optimized in-sample often underperform the naïve (equal weights) allocation out-of-sample. This instability can be traced back to two sources: (i) noise in the input variables; and (ii) signal structure that magnifies the estimation errors in the input variables. The paper by Lopez de Prado ([source](https://papers.ssrn.com/sol3/papers.cfm?abstract_id=3469961)) introduces the nested clustered optimization algorithm (NCO), a method that tackles both sources of instability.

```
optional arguments:
  -p HISTORIC_PERIOD, --period HISTORIC_PERIOD
                        Period to get yfinance data from. Possible frequency
                        strings are: 'd': means days, for example '252d' means
                        252 days 'w': means weeks, for example '52w' means 52
                        weeks 'mo': means months, for example '12mo' means 12
                        months 'y': means years, for example '1y' means 1 year
                        'ytd': downloads data from beginning of year to today
                        'max': downloads all data available for each asset
                        (default: 3y)
  -s START_PERIOD, --start START_PERIOD
                        Start date to get yfinance data from. Must be in
                        'YYYY-MM-DD' format (default: )
  -e END_PERIOD, --end END_PERIOD
                        End date to get yfinance data from. Must be in 'YYYY-
                        MM-DD' format (default: )
  -lr, --log-returns    If use logarithmic or arithmetic returns to calculate
                        returns (default: False)
  -f {d,w,m}, --freq {d,w,m}
                        Frequency used to calculate returns. Possible values
                        are: 'd': for daily returns 'w': for weekly returns
                        'm': for monthly returns (default: d)
  -mn MAX_NAN, --maxnan MAX_NAN
                        Max percentage of nan values accepted per asset to be
                        considered in the optimization process (default: 0.05)
  -th THRESHOLD_VALUE, --threshold THRESHOLD_VALUE
                        Value used to replace outliers that are higher to
                        threshold in absolute value (default: 0.3)
  -mt NAN_FILL_METHOD, --method NAN_FILL_METHOD
                        Method used to fill nan values in time series, by
                        default time. Possible values are: 'linear': linear
                        interpolation 'time': linear interpolation based on
                        time index 'nearest': use nearest value to replace nan
                        values 'zero': spline of zeroth order 'slinear':
                        spline of first order 'quadratic': spline of second
                        order 'cubic': spline of third order 'barycentric':
                        builds a polynomial that pass for all points (default:
                        time)
  -cd {pearson,spearman,abs_pearson,abs_spearman,distance,mutual_info,tail}, --codependence {pearson,spearman,abs_pearson,abs_spearman,distance,mutual_info,tail}
                        The codependence or similarity matrix used to build
                        the distance metric and clusters. Possible values are:
                        'pearson': pearson correlation matrix 'spearman':
                        spearman correlation matrix 'abs_pearson': absolute
                        value of pearson correlation matrix 'abs_spearman':
                        absolute value of spearman correlation matrix
                        'distance': distance correlation matrix 'mutual_info':
                        mutual information codependence matrix 'tail': tail
                        index codependence matrix (default: pearson)
  -cv {hist,ewma1,ewma2,ledoit,oas,shrunk,gl,jlogo,fixed,spectral,shrink}, --covariance {hist,ewma1,ewma2,ledoit,oas,shrunk,gl,jlogo,fixed,spectral,shrink}
                        Method used to estimate covariance matrix. Possible
                        values are 'hist': historical method 'ewma1':
                        exponential weighted moving average with adjust=True
                        'ewma2': exponential weighted moving average with
                        adjust=False 'ledoit': Ledoit and Wolf shrinkage
                        method 'oas': oracle shrinkage method 'shrunk':
                        scikit-learn shrunk method 'gl': graphical lasso
                        method 'jlogo': j-logo covariance 'fixed': takes
                        average of eigenvalues above max Marchenko Pastour
                        limit 'spectral': makes zero eigenvalues above max
                        Marchenko Pastour limit 'shrink': Lopez de Prado's
                        book shrinkage method (default: hist)
  -o {MinRisk,Utility,Sharpe,ERC}, --objective {MinRisk,Utility,Sharpe,ERC}
                        Objective function used to optimize the portfolio
                        (default: MinRisk)
  -rm {MV,MAD,MSV,FLPM,SLPM,CVaR,EVaR,WR,ADD,UCI,CDaR,EDaR,MDD}, --risk-measure {MV,MAD,MSV,FLPM,SLPM,CVaR,EVaR,WR,ADD,UCI,CDaR,EDaR,MDD}
                        Risk measure used to optimize the portfolio. Possible
                        values are: 'MV' : Variance 'MAD' : Mean Absolute
                        Deviation 'MSV' : Semi Variance (Variance of negative
                        returns) 'FLPM' : First Lower Partial Moment 'SLPM' :
                        Second Lower Partial Moment 'CVaR' : Conditional Value
                        at Risk 'EVaR' : Entropic Value at Risk 'WR' : Worst
                        Realization 'ADD' : Average Drawdown of uncompounded
                        returns 'UCI' : Ulcer Index of uncompounded returns
                        'CDaR' : Conditional Drawdown at Risk of uncompounded
                        returns 'EDaR' : Entropic Drawdown at Risk of
                        uncompounded returns 'MDD' : Maximum Drawdown of
                        uncompounded returns (default: MV)
  -r RISK_FREE, --risk-free-rate RISK_FREE
                        Risk-free rate of borrowing/lending. The period of the
                        risk-free rate must be annual (default: 0.00329)
  -ra RISK_AVERSION, --risk-aversion RISK_AVERSION
                        Risk aversion parameter (default: 1)
  -a SIGNIFICANCE_LEVEL, --alpha SIGNIFICANCE_LEVEL
                        Significance level of CVaR, EVaR, CDaR and EDaR
                        (default: 0.05)
  -lk {single,complete,average,weighted,centroid,median,ward,dbht}, --linkage {single,complete,average,weighted,centroid,median,ward,dbht}
                        Linkage method of hierarchical clustering (default:
                        single)
  -k AMOUNT_CLUSTERS    Number of clusters specified in advance (default:
                        None)
  -mk MAX_CLUSTERS, --max-k MAX_CLUSTERS
                        Max number of clusters used by the two difference gap
                        statistic to find the optimal number of clusters. If k
                        is empty this value is used (default: 10)
  -bi AMOUNT_BINS, --bins-info AMOUNT_BINS
                        Number of bins used to calculate the variation of
                        information (default: KN)
  -at ALPHA_TAIL, --alpha-tail ALPHA_TAIL
                        Significance level for lower tail dependence index,
                        only used when when codependence value is 'tail'
                        (default: 0.05)
  -lo, --leaf-order     indicates if the cluster are ordered so that the
                        distance between successive leaves is minimal
                        (default: True)
  -de SMOOTHING_FACTOR_EWMA, --d-ewma SMOOTHING_FACTOR_EWMA
                        Smoothing factor for ewma estimators (default: 0.94)
  -v LONG_ALLOCATION, --value LONG_ALLOCATION
                        Amount to allocate to portfolio (default: 1)
  --name NAME           Save portfolio with personalized or default name
                        (default: NCO_0)
  -h, --help            show this help message (default: False)
```

Example:
```
2022 Apr 05, 14:34 (🦋) /portfolio/po/ $ nco

 [3 Years] Nested clustered optimization using pearson codependence,
single linkage and volatility as risk measure

     Weights      
┏━━━━━━┳━━━━━━━━━┓
┃      ┃ Value   ┃
┡━━━━━━╇━━━━━━━━━┩
│ AAPL │  7.17 % │
├──────┼─────────┤
│ AMZN │ 19.33 % │
├──────┼─────────┤
│ BA   │  0.0 %  │
├──────┼─────────┤
│ FB   │  0.53 % │
├──────┼─────────┤
│ MSFT │ 16.81 % │
├──────┼─────────┤
│ T    │ 56.14 % │
├──────┼─────────┤
│ TSLA │  0.0 %  │
└──────┴─────────┘

Annual (by 252) expected return: 15.58%
Annual (by √252) volatility: 22.42%
Sharpe ratio: 0.6868
```