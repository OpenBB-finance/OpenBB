```
usage: info [-h]
```
Show information of custom data.

```
optional arguments:
  -h, --help  show this help message (default: False)
```

Sample Output:
```python
<class 'pandas.core.frame.DataFrame'>
DatetimeIndex: 732 entries, 2020-01-01 to 2022-01-01
Data columns (total 4 columns):
 #   Column    Non-Null Count  Dtype  
---  ------    --------------  -----  
 0   colnorm   732 non-null    float64
 1   col2      732 non-null    float64
 2   colnorm3  732 non-null    float64
 3   colb      732 non-null    float64
dtypes: float64(4)
memory usage: 28.6 KB
None
```

This tells us the loaded dataframe, (which there is one saved as a default template as test.csv)
has 4 columns that are all floats (numeric).  The index is a date time range from the start of 2020 to the start of 2022.
