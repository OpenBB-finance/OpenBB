```
usage: show [-s SORTCOL [SORTCOL ...]] [-a] [-h] [-l LIMIT]
```
Show loaded dataframe
```
optional arguments:
  -s SORTCOL [SORTCOL ...], --sortcol SORTCOL [SORTCOL ...]
  -a, --ascend
  -h, --help            show this help message (default: False)
  -l LIMIT, --limit LIMIT
                        Number of entries to show in data. (default: 5)
```

Sample Output:
```
2022 Jan 18, 17:53 (✨) /custom/ $ show -l 3
             colnorm      col2  colnorm3      colb
date                                              
2020-01-01  0.999953  1.012313  1.008667  0.001203
2020-01-02  0.983850  1.023421  1.004225  0.004517
2020-01-03  1.002692  1.019749  1.006244  0.007035
```

This shows the top 3 rows of my custom dataframe.  This should primarily be used as a method of debugging that the load worked.