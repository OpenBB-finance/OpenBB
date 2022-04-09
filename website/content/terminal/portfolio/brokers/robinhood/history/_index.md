```
usage: history [-s {day,week,month,3month,year,5year,all}] [-i {5minute,10minute,hour,day,week}]
               [--export {csv,json,xlsx}] [-h]
```
Historical Portfolio Info
```
optional arguments:
  -s {day,week,month,3month,year,5year,all}, --span {day,week,month,3month,year,5year,all}
                        Span of historical data (default: 3month)
  -i {5minute,10minute,hour,day,week}, --interval {5minute,10minute,hour,day,week}
                        Interval to look at portfolio (default: day)
  --export {csv,json,xlsx}
                        Export dataframe data to csv,json,xlsx file (default: )
  -h, --help            show this help message (default: False)
```

Sample Output:

![RH_hist](https://user-images.githubusercontent.com/18151143/134234686-47ffdcf7-0c69-4557-a554-578d6c125a16.png)
