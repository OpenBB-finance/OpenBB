```
usage: volexch [--raw] [-s {,NetShort,Date,TotalVolume,PctShort}] [-a] [-m] [-h] [--export {png,jpg,pdf,svg}]
```

Displays short volume based on exchange.

This data is pulled from the NYSE daily.  When updating data, this command may not not be available.

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
<img size="1400" alt="Feature Screenshot - volexch" src="https://user-images.githubusercontent.com/85772166/142969080-6b6fdee9-068f-4f7b-9240-463c69056f97.png">

