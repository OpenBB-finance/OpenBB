```
usage: ftd [-s START] [-e END] [-n N_NUM] [--raw] [--export {csv,json,xlsx}] [-h]
```
Display Fails to Deliver statistics for the [loaded ticker](https://gamestonkterminal.github.io/GamestonkTerminal/stocks/load/). Source: https://www.sec.gov/data/foiadocsfailsdatahtm

For an in-depth look at the complex iregularities of the securities settlement process, review this PDF:
[Naked Short Sales and Fails to Deliver: An Overview of Clearing and Settlement Procedures for Stock Trades in the US](https://github.com/deeleeramone/GamestonkTerminal/files/7489219/Naked.Short.Sales.and.Fails.to.Deliver.pdf)

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
<img width="1337" alt="Feature Screenshot - FTD" src="https://user-images.githubusercontent.com/85772166/140587710-02d97bbe-d75c-4489-8411-e051e7d802a6.png">

<img width="1400" alt="Feature Screenshot - ftd raw" src="https://user-images.githubusercontent.com/85772166/140587632-bd97eb1c-3f79-4537-a86e-5b22042a365e.png">

