```
usage: long [-p PICK [PICK ...]] [-a AMOUNT] [-h]

This function plots option hedge diagrams

optional arguments:
  -p PICK [PICK ...], --pick PICK [PICK ...]
                        Choose what you would like to pick (default: None)
  -a AMOUNT, --amount AMOUNT
                        Choose the amount invested (default: 1000)
  -h, --help            show this help message (default: False)
```

Example
```
2022 May 10, 09:21 (🦋) /stocks/options/hedge/ $ pick 170 Short Call -a 500
2022 May 10, 09:22 (🦋) /stocks/options/hedge/ $ help
╭──────────────────────Stocks - Options - Hedge ─────────────────────────╮      
│ Ticker:                                                                |
AAPL                                                                     |
│ Expiry:                                                                | 2022-05-13          |                                                                         
│     pick          pick the underlying asset position   
│                                                                                  
│ Underlying Asset Position: Short Call 500 @ 170 
│  
│     list          show the available strike prices for calls and puts 
│     add           add an option to the list of options  
│     rmv           remove an option from the list of options 
│     sop           show selected options and neutral portfolio weights 
|
╰──────────────────────────────────────────────────────OpenBB Terminal ─╯
```