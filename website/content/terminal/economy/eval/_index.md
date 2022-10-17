```
usage: eval [-q QUERY [QUERY ...]] [-h] [--export EXPORT]
```
Create custom data column from loaded datasets.

Note that for division, the / operator will cause issues, so one should do `*N**-1` where N is the number you are dividing by 
```
options:
  -q QUERY [QUERY ...], --query QUERY [QUERY ...]
  -h, --help            show this help message (default: False)
  --export EXPORT       Export raw data into csv, json, xlsx (default: )
```
For more information and examples, use 'about eval' to access the related guide.
