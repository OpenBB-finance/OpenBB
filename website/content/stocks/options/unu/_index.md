```
usage: unu [-n NUM] [--sortby {Option,Vol/OI,Vol,OI,Bid,Ask}] [-a] [--export {csv,json,xlsx}] [-h]
```

See unusual options activity and sort by the available columns. Source: https://fdsscanner.com

```
optional arguments:
  -n NUM, --num NUM     Number of options to show. Each scraped page gives 20 results. (default: 20)
  --sortby {Option,Vol/OI,Vol,OI,Bid,Ask}
                        Column to sort by. Vol/OI is the default and typical variable to be considered unusual. (default: Vol/OI)
  -a, --ascending       Flag to sort in ascending order (default: False)
  --export {csv,json,xlsx}
                        Export dataframe data to csv,json,xlsx file (default: )
  -h, --help            show this help message (default: False)
```
<img size="1400" alt="Feature Screenshot - unu" src="https://user-images.githubusercontent.com/85772166/142510525-f9f1b40a-0188-4561-9b85-6e968d6ecdcd.png">
