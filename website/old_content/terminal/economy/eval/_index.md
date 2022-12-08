```
usage: eval [-q QUERY [QUERY ...]] [-h] [--export EXPORT]
```
Create custom data column from loaded datasets. Can be mathematical expressions supported by pandas.eval() function.
Example. If I have loaded `fred DGS2,DGS5` and I want to create a new column that is the difference between these two,
I can create a new column by doing `eval spread = DGS2 - DGS5`.

Notice that the command is case sensitive, i.e., `DGS2` is not the same as `dgs2`.

Note that for division, the / operator will cause issues, so one should do `*N**-1` where N is the number you are dividing by
```
options:
  -q QUERY [QUERY ...], --query QUERY [QUERY ...]
  -h, --help            show this help message (default: False)
  --export EXPORT       Export raw data into csv, json, xlsx (default: )
```
