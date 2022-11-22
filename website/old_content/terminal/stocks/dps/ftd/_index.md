```
usage: ftd [-s START] [-e END] [-n N_NUM] [--raw] [--export {csv,json,xlsx}] [-h]
```

Display Fails to Deliver statistics for the loaded ticker. Source: https://www.sec.gov/data/foiadocsfailsdatahtm

```
optional arguments:
  -s START, --start START
                        start of datetime to see FTD
  -e END, --end END     end of datetime to see FTD
  -n N_NUM, --num N_NUM
                        number of latest fails-to-deliver being printed
  --raw                 Print raw data.
  --export {csv,json,xlsx}
                        Export dataframe data to csv,json,xlsx file
  -h, --help            show this help message
```

![ftd](https://user-images.githubusercontent.com/46355364/154075166-a5a84604-e8ec-46d5-a990-8ca3d928c662.png)
