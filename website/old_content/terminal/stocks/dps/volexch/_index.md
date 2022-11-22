```
usage: volexch [-r] [-s {,NetShort,Date,TotalVolume,PctShort}] [-a] [-p] [-h] [--export {csv,json,xlsx,png,jpg,pdf,svg}]
```

Displays short volume across lit NYSE venues. This data is updated nightly, this command may not not be available during updates.

```
optional arguments:
  -r, --raw             Display raw data
  -s {,NetShort,Date,TotalVolume,PctShort}, --sort {,NetShort,Date,TotalVolume,PctShort}
                        Column to sort by
  -a, --asc             Sort in ascending order
  -p, --plotly          Display plot using interactive plotly.
  -h, --help            show this help message
  --export {csv,json,xlsx,png,jpg,pdf,svg}
                        Export raw data into csv, json, xlsx and figure into png, jpg, pdf, svg
```

![volexch](https://user-images.githubusercontent.com/46355364/154225329-3e3d82a5-8bf4-4fbe-b1c5-d76a8c04a0a0.png)
