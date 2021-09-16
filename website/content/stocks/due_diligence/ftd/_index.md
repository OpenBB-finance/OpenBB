```text
usage: ftd [-s START] [-e END] [-n N_NUM] [--raw] [--export {csv,json,xlsx}]
```

The fails-to-deliver data collected by SEC. Fails to deliver on a given day are a cumulative number of all fails outstanding until that day, plus new fails that occur that day, less fails that settle that day. See <https://www.sec.gov/data/foiadocsfailsdatahtm>. Note that FTD is 1 month delayed. [Source: SEC]

* -n : number of latest fails-to-deliver being printed. Default 0. Overrules start and end FTD datetime.
* -s : start of datetime to see FTD. Default 20 days in past.
* -e : end of datetime to see FTD. Default today.
* --raw : Print raw data.
* --export : Export dataframe data to csv,json,xlsx file

![ftd](https://user-images.githubusercontent.com/25267873/125202513-d520b280-e26b-11eb-8091-5b221636a5ce.png)
