```
usage: options [-n {NAME}] [-h] [--export {csv,json,xlsx}]
```

Show the column-dataset combination that can be entered within the different functions.

```
optional arguments:
  -n {NAME}, --name {NAME} 
                        The dataset you would like to show the options for (default: None)
  -h, --help            show this help message (default: False)
  --export {csv,json,xlsx}
                        Export raw data into csv, json, xlsx (default: )
```

Example:
```
2022 Feb 28, 04:26 (✨) /econometrics/ $ options
            Options for msft
┏━━━━━━━━━┳━━━━━━━━━━━┳━━━━━━━━━━━━━━━━┓
┃ dataset ┃ column    ┃ option         ┃
┡━━━━━━━━━╇━━━━━━━━━━━╇━━━━━━━━━━━━━━━━┩
│ msft    │ date      │ date-msft      │
├─────────┼───────────┼────────────────┤
│ msft    │ open      │ open-msft      │
├─────────┼───────────┼────────────────┤
│ msft    │ high      │ high-msft      │
├─────────┼───────────┼────────────────┤
│ msft    │ low       │ low-msft       │
├─────────┼───────────┼────────────────┤
│ msft    │ close     │ close-msft     │
├─────────┼───────────┼────────────────┤
│ msft    │ adj_close │ adj_close-msft │
├─────────┼───────────┼────────────────┤
│ msft    │ volume    │ volume-msft    │
└─────────┴───────────┴────────────────┘
          Options for ll
┏━━━━━━━━━┳━━━━━━━━━┳━━━━━━━━━━━━┓
┃ dataset ┃ column  ┃ option     ┃
┡━━━━━━━━━╇━━━━━━━━━╇━━━━━━━━━━━━┩
│ ll      │ totemp  │ totemp-ll  │
├─────────┼─────────┼────────────┤
│ ll      │ gnpdefl │ gnpdefl-ll │
├─────────┼─────────┼────────────┤
│ ll      │ gnp     │ gnp-ll     │
├─────────┼─────────┼────────────┤
│ ll      │ unemp   │ unemp-ll   │
├─────────┼─────────┼────────────┤
│ ll      │ armed   │ armed-ll   │
├─────────┼─────────┼────────────┤
│ ll      │ pop     │ pop-ll     │
├─────────┼─────────┼────────────┤
│ ll      │ year    │ year-ll    │
└─────────┴─────────┴────────────┘
           Options for a96
┏━━━━━━━━━┳━━━━━━━━━━┳━━━━━━━━━━━━━━┓
┃ dataset ┃ column   ┃ option       ┃
┡━━━━━━━━━╇━━━━━━━━━━╇━━━━━━━━━━━━━━┩
│ a96     │ popul    │ popul-a96    │
├─────────┼──────────┼──────────────┤
│ a96     │ tvnews   │ tvnews-a96   │
├─────────┼──────────┼──────────────┤
│ a96     │ selflr   │ selflr-a96   │
├─────────┼──────────┼──────────────┤
│ a96     │ clinlr   │ clinlr-a96   │
├─────────┼──────────┼──────────────┤
│ a96     │ dolelr   │ dolelr-a96   │
├─────────┼──────────┼──────────────┤
│ a96     │ pid      │ pid-a96      │
├─────────┼──────────┼──────────────┤
│ a96     │ age      │ age-a96      │
├─────────┼──────────┼──────────────┤
│ a96     │ educ     │ educ-a96     │
├─────────┼──────────┼──────────────┤
│ a96     │ income   │ income-a96   │
├─────────┼──────────┼──────────────┤
│ a96     │ vote     │ vote-a96     │
├─────────┼──────────┼──────────────┤
│ a96     │ logpopul │ logpopul-a96 │
└─────────┴──────────┴──────────────┘

2022 Feb 28, 04:27 (✨) /econometrics/ $ options ll
          Options for ll
┏━━━━━━━━━┳━━━━━━━━━┳━━━━━━━━━━━━┓
┃ dataset ┃ column  ┃ option     ┃
┡━━━━━━━━━╇━━━━━━━━━╇━━━━━━━━━━━━┩
│ ll      │ totemp  │ totemp-ll  │
├─────────┼─────────┼────────────┤
│ ll      │ gnpdefl │ gnpdefl-ll │
├─────────┼─────────┼────────────┤
│ ll      │ gnp     │ gnp-ll     │
├─────────┼─────────┼────────────┤
│ ll      │ unemp   │ unemp-ll   │
├─────────┼─────────┼────────────┤
│ ll      │ armed   │ armed-ll   │
├─────────┼─────────┼────────────┤
│ ll      │ pop     │ pop-ll     │
├─────────┼─────────┼────────────┤
│ ll      │ year    │ year-ll    │
└─────────┴─────────┴────────────┘
```
