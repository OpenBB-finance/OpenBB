```
usage: herc [-p HISTORIC_PERIOD] [-s START_PERIOD] [-e END_PERIOD] [-lr]
            [-f {d,w,m}] [-mn MAX_NAN] [-th THRESHOLD_VALUE]
            [-mt NAN_FILL_METHOD]
            [-cd {pearson,spearman,abs_pearson,abs_spearman,distance,mutual_info,tail}]
            [-cv {hist,ewma1,ewma2,ledoit,oas,shrunk,gl,jlogo,fixed,spectral,shrink}]
            [-rm {MV,MAD,GMD,MSV,VaR,CVaR,TG,EVaR,RG,CVRG,TGRG,WR,FLPM,SLPM,MDD,ADD,DaR,CDaR,EDaR,UCI,MDD_Rel,ADD_Rel,DaR_Rel,CDaR_Rel,EDaR_Rel,UCI_Rel}]
            [-r RISK_FREE] [-a SIGNIFICANCE_LEVEL]
            [-as CVAR_SIMULATIONS_LOSSES] [-b CVAR_SIGNIFICANCE]
            [-bs CVAR_SIMULATIONS_GAINS]
            [-lk {single,complete,average,weighted,centroid,median,ward,dbht}]
            [-k AMOUNT_CLUSTERS] [-mk MAX_CLUSTERS] [-bi AMOUNT_BINS]
            [-at ALPHA_TAIL] [-lo LEAF_ORDER] [-de SMOOTHING_FACTOR_EWMA]
            [-v LONG_ALLOCATION] [--name NAME] [-h]
```

In a risk budgeting portfolio, the risk contribution from each component is equal to the budget of risk defined by the portfolio manager. Maillard, Roncalli, and Teiletche ([source](https://investresolve.com/portfolio-optimization-simple-optimal-methods/#ref-Maillard2008)) described the Equal Risk Contribution optimization, which is satisfied when all assets contribute the same volatility to the portfolio (equal risk budgeting). It has been shown that the Equal Risk Contribution portfolio is a compelling balance between the objectives of the equal weight and Minimum Variance portfolios. It is also a close cousin to the Inverse Volatility portfolio, except that it is less vulnerable to the case where assets have vastly different correlations.

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
  -rm {MV,MAD,GMD,MSV,VaR,CVaR,TG,EVaR,RG,CVRG,TGRG,WR,FLPM,SLPM,MDD,ADD,DaR,CDaR,EDaR,UCI,MDD_Rel,ADD_Rel,DaR_Rel,CDaR_Rel,EDaR_Rel,UCI_Rel}, --risk-measure {MV,MAD,GMD,MSV,VaR,CVaR,TG,EVaR,RG,CVRG,TGRG,WR,FLPM,SLPM,MDD,ADD,DaR,CDaR,EDaR,UCI,MDD_Rel,ADD_Rel,DaR_Rel,CDaR_Rel,EDaR_Rel,UCI_Rel}
                        Risk measure used to optimize the portfolio. Possible
                        values are: 'MV' : Variance 'MAD' : Mean Absolute
                        Deviation 'GMD' : Gini Mean Difference 'MSV' : Semi
                        Variance (Variance of negative returns) 'FLPM' : First
                        Lower Partial Moment 'SLPM' : Second Lower Partial
                        Moment 'VaR' : Value at Risk 'CVaR' : Conditional
                        Value at Risk 'TG' : Tail Gini 'EVaR' : Entropic Value
                        at Risk 'WR' : Worst Realization 'RG' : Range 'CVRG' :
                        CVaR Range 'TGRG' : Tail Gini Range 'ADD' : Average
                        Drawdown of uncompounded returns 'UCI' : Ulcer Index
                        of uncompounded returns 'DaR' : Drawdown at Risk of
                        uncompounded returns 'CDaR' : Conditional Drawdown at
                        Risk of uncompounded returns 'EDaR' : Entropic
                        Drawdown at Risk of uncompounded returns 'MDD' :
                        Maximum Drawdown of uncompounded returns 'ADD_Rel' :
                        Average Drawdown of compounded returns 'UCI_Rel' :
                        Ulcer Index of compounded returns 'DaR_Rel' : Drawdown
                        at Risk of compounded returns 'CDaR_Rel' : Conditional
                        Drawdown at Risk of compounded returns 'EDaR_Rel' :
                        Entropic Drawdown at Risk of compounded returns
                        'MDD_Rel' : Maximum Drawdown of compounded returns
                        (default: MV)
  -r RISK_FREE, --risk-free-rate RISK_FREE
                        Risk-free rate of borrowing/lending. The period of the
                        risk-free rate must be annual (default: 0.00329)
  -a SIGNIFICANCE_LEVEL, --alpha SIGNIFICANCE_LEVEL
                        Significance level of VaR, CVaR, EVaR, DaR, CDaR, EDaR
                        and Tail Gini of losses (default: 0.05)
  -as CVAR_SIMULATIONS_LOSSES, --a-sim CVAR_SIMULATIONS_LOSSES
                        Number of CVaRs used to approximate Tail Gini of
                        losses. The default is 100 (default: 100)
  -b CVAR_SIGNIFICANCE, --beta CVAR_SIGNIFICANCE
                        Significance level of CVaR and Tail Gini of gains. If
                        empty it duplicates alpha (default: None)
  -bs CVAR_SIMULATIONS_GAINS, --b-sim CVAR_SIMULATIONS_GAINS
                        Number of CVaRs used to approximate Tail Gini of
                        gains. If empty it duplicates a_sim value (default:
                        None)
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
  -lo LEAF_ORDER, --leaf-order LEAF_ORDER
                        Indicates if the cluster are ordered so that the
                        distance between successive leaves is minimal
                        (default: True)
  -de SMOOTHING_FACTOR_EWMA, --d-ewma SMOOTHING_FACTOR_EWMA
                        Smoothing factor for ewma estimators (default: 0.94)
  -v LONG_ALLOCATION, --value LONG_ALLOCATION
                        Amount to allocate to portfolio (default: 1)
  --name NAME           Save portfolio with personalized or default name
                        (default: HERC_0)
  -h, --help            show this help message (default: False)
```

Example:
```
2022 Apr 05, 14:40 (🦋) /portfolio/po/ $ herc

 [3 Years] Hierarchical equal risk contribution portfolio using pearson
codependence,single linkage and volatility as risk measure

     Weights      
┏━━━━━━┳━━━━━━━━━┓
┃      ┃ Value   ┃
┡━━━━━━╇━━━━━━━━━┩
│ AAPL │ 10.78 % │
├──────┼─────────┤
│ AMZN │ 12.64 % │
├──────┼─────────┤
│ BA   │  9.12 % │
├──────┼─────────┤
│ FB   │  8.08 % │
├──────┼─────────┤
│ MSFT │ 12.86 % │
├──────┼─────────┤
│ T    │ 43.83 % │
├──────┼─────────┤
│ TSLA │  2.66 % │
└──────┴─────────┘

Annual (by 252) expected return: 18.09%
Annual (by √252) volatility: 24.19%
Sharpe ratio: 0.7401
```