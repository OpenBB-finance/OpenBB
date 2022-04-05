```
usage: nco [-p PERIOD] [-s START] [-e END] [-lr] [-f {d,w,m}] [-mn MAXNAN]
           [-th THRESHOLD] [-mt METHOD]
           [-cd {pearson,spearman,abs_pearson,abs_spearman,distance,mutual_info,tail}]
           [-cv {hist,ewma1,ewma2,ledoit,oas,shrunk,gl,jlogo,fixed,spectral,shrink}]
           [-o {MinRisk,Utility,Sharpe,ERC}]
           [-rm {MV,MAD,GMD,MSV,VaR,CVaR,TG,EVaR,RG,CVRG,TGRG,WR,FLPM,SLPM,MDD,ADD,DaR,CDaR,EDaR,UCI,MDD_Rel,ADD_Rel,DaR_Rel,CDaR_Rel,EDaR_Rel,UCI_Rel}]
           [-r RISK_FREE_RATE] [-ra RISK_AVERSION] [-a ALPHA]
           [-lk {single,complete,average,weighted,centroid,median,ward,dbht}]
           [-k K] [-mk MAX_K] [-bi BINS_INFO] [-at ALPHA_TAIL] [-lo]
           [-de D_EWMA] [-v VALUE] [--pie] [--hist] [--dd] [--rc-chart]
           [--heat] [-h]
```

Builds a nested clustered optimization portfolio.

```
optional arguments:
  -p PERIOD, --period PERIOD
                        Period to get yfinance data from (default: 3y)
  -s START, --start START
                        Start date to get yfinance data from (default: )
  -e END, --end END     End date to get yfinance data from (default: )
  -lr, --log-returns    If use logarithmic or arithmetic returns to calculate
                        returns (default: False)
  -f {d,w,m}, --freq {d,w,m}
                        Frequency used to calculate returns (default: d)
  -mn MAXNAN, --maxnan MAXNAN
                        Max percentage of nan values accepted per asset to be
                        considered in the optimization process (default: 0.05)
  -th THRESHOLD, --threshold THRESHOLD
                        Value used to replace outliers that are higher to
                        threshold in absolute value (default: 0.3)
  -mt METHOD, --method METHOD
                        Method used to fill nan values (default: time)
  -cd {pearson,spearman,abs_pearson,abs_spearman,distance,mutual_info,tail}, --codependence {pearson,spearman,abs_pearson,abs_spearman,distance,mutual_info,tail}
                        The codependence or similarity matrix used to build
                        the distance metric and clusters (default: pearson)
  -cv {hist,ewma1,ewma2,ledoit,oas,shrunk,gl,jlogo,fixed,spectral,shrink}, --covariance {hist,ewma1,ewma2,ledoit,oas,shrunk,gl,jlogo,fixed,spectral,shrink}
                        The codependence or similarity matrix used to build
                        the distance metric and clusters (default: hist)
  -o {MinRisk,Utility,Sharpe,ERC}, --objective {MinRisk,Utility,Sharpe,ERC}
                        Objective function used to optimize the portfolio
                        (default: MinRisk)
  -rm {MV,MAD,GMD,MSV,VaR,CVaR,TG,EVaR,RG,CVRG,TGRG,WR,FLPM,SLPM,MDD,ADD,DaR,CDaR,EDaR,UCI,MDD_Rel,ADD_Rel,DaR_Rel,CDaR_Rel,EDaR_Rel,UCI_Rel}, --risk-measure {MV,MAD,GMD,MSV,VaR,CVaR,TG,EVaR,RG,CVRG,TGRG,WR,FLPM,SLPM,MDD,ADD,DaR,CDaR,EDaR,UCI,MDD_Rel,ADD_Rel,DaR_Rel,CDaR_Rel,EDaR_Rel,UCI_Rel}
                        Risk measure used to optimize the portfolio (default:
                        MV)
  -r RISK_FREE_RATE, --risk-free-rate RISK_FREE_RATE
                        Risk-free rate of borrowing/lending. The period of the
                        risk-free rate must be annual (default: 0.00185)
  -ra RISK_AVERSION, --risk-aversion RISK_AVERSION
                        Risk aversion parameter (default: 1.0)
  -a ALPHA, --alpha ALPHA
                        Significance level of CVaR, EVaR, CDaR and EDaR
                        (default: 0.05)
  -lk {single,complete,average,weighted,centroid,median,ward,dbht}, --linkage {single,complete,average,weighted,centroid,median,ward,dbht}
                        Linkage method of hierarchical clustering (default:
                        single)
  -k K                  Number of clusters specified in advance (default: )
  -mk MAX_K, --max-k MAX_K
                        Max number of clusters used by the two difference gap
                        statistic to find the optimal number of clusters. If k
                        is empty this value is used (default: 10)
  -bi BINS_INFO, --bins-info BINS_INFO
                        Number of bins used to calculate the variation of
                        information (default: KN)
  -at ALPHA_TAIL, --alpha-tail ALPHA_TAIL
                        Significance level for lower tail dependence index,
                        only used when when codependence value is 'tail'
                        (default: 0.05)
  -lo, --leaf-order     indicates if the cluster are ordered so that the
                        distance between successive leaves is minimal
                        (default: True)
  -de D_EWMA, --d-ewma D_EWMA
                        Smoothing factor for ewma estimators (default: 0.94)
  -v VALUE, --value VALUE
                        Amount to allocate to portfolio (default: 1.0)
  --pie                 Display a pie chart for weights (default: False)
  --hist                Display a histogram with risk measures (default:
                        False)
  --dd                  Display a drawdown chart with risk measures (default:
                        False)
  --rc-chart            Display a risk contribution chart for assets (default:
                        False)
  --heat                Display a heatmap of correlation matrix with
                        dendrogram (default: False)
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