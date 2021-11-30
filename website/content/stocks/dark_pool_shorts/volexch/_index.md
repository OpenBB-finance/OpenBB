```
usage: volexch [--raw] [-s {,NetShort,Date,TotalVolume,PctShort}] [-a] [-m] [-h] [--export {png,jpg,pdf,svg}]
```

Displays short volume across lit NYSE venues. This data is updated nightly, this command may not not be available during updates.

```
optional arguments:
  --raw                 Display raw data
  -s {,NetShort,Date,TotalVolume,PctShort}, --sort {,NetShort,Date,TotalVolume,PctShort}
                        Column to sort by
  -a, --asc             Sort in ascending order
  -m, --mpl             Display plot using matplotlb.
  -h, --help            show this help message
  --export {png,jpg,pdf,svg}
                        Export or figure into png, jpg, pdf, svg
```
<img size="1400" alt="Feature Screenshot - volexch" src="https://user-images.githubusercontent.com/85772166/144008682-e5ddf0b3-b99b-4bb0-9e7d-1eb235f89f21.png">

