```
usage: options [-n {}] [-h]
```

Show the column-dataset combination that can be entered within the functions.

```
optional arguments:
  -n {}, --name {}  The dataset you would like to show the options for (default: None)
  -h, --help        show this help message (default: False)
```

Example:
```
2022 Feb 24, 04:40 (✨) /statistics/ $ options
            Options for aapl            
┏━━━━━━━━━┳━━━━━━━━━━━┳━━━━━━━━━━━━━━━━┓
┃ dataset ┃ column    ┃ option         ┃
┡━━━━━━━━━╇━━━━━━━━━━━╇━━━━━━━━━━━━━━━━┩
│ aapl    │ open      │ open-aapl      │
├─────────┼───────────┼────────────────┤
│ aapl    │ high      │ high-aapl      │
├─────────┼───────────┼────────────────┤
│ aapl    │ low       │ low-aapl       │
├─────────┼───────────┼────────────────┤
│ aapl    │ close     │ close-aapl     │
├─────────┼───────────┼────────────────┤
│ aapl    │ adj_close │ adj_close-aapl │
├─────────┼───────────┼────────────────┤
│ aapl    │ volume    │ volume-aapl    │
└─────────┴───────────┴────────────────┘

                      Options for thesis                      
┏━━━━━━━━━┳━━━━━━━━━━━━━━━━━━━━━┳━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓
┃ dataset ┃ column              ┃ option                     ┃
┡━━━━━━━━━╇━━━━━━━━━━━━━━━━━━━━━╇━━━━━━━━━━━━━━━━━━━━━━━━━━━━┩
│ thesis  │ company             │ company-thesis             │
├─────────┼─────────────────────┼────────────────────────────┤
│ thesis  │ current_assets      │ current_assets-thesis      │
├─────────┼─────────────────────┼────────────────────────────┤
│ thesis  │ assets              │ assets-thesis              │
├─────────┼─────────────────────┼────────────────────────────┤
│ thesis  │ debt                │ debt-thesis                │
├─────────┼─────────────────────┼────────────────────────────┤
│ thesis  │ depr_amor           │ depr_amor-thesis           │
├─────────┼─────────────────────┼────────────────────────────┤
│ thesis  │ income              │ income-thesis              │
├─────────┼─────────────────────┼────────────────────────────┤
│ thesis  │ current_liabilities │ current_liabilities-thesis │
├─────────┼─────────────────────┼────────────────────────────┤
│ thesis  │ revenue             │ revenue-thesis             │
├─────────┼─────────────────────┼────────────────────────────┤
│ thesis  │ equity              │ equity-thesis              │
├─────────┼─────────────────────┼────────────────────────────┤
│ thesis  │ interest_expense    │ interest_expense-thesis    │
└─────────┴─────────────────────┴────────────────────────────┘

2022 Feb 24, 04:40 (✨) /statistics/ $ options aapl
            Options for aapl            
┏━━━━━━━━━┳━━━━━━━━━━━┳━━━━━━━━━━━━━━━━┓
┃ dataset ┃ column    ┃ option         ┃
┡━━━━━━━━━╇━━━━━━━━━━━╇━━━━━━━━━━━━━━━━┩
│ aapl    │ open      │ open-aapl      │
├─────────┼───────────┼────────────────┤
│ aapl    │ high      │ high-aapl      │
├─────────┼───────────┼────────────────┤
│ aapl    │ low       │ low-aapl       │
├─────────┼───────────┼────────────────┤
│ aapl    │ close     │ close-aapl     │
├─────────┼───────────┼────────────────┤
│ aapl    │ adj_close │ adj_close-aapl │
├─────────┼───────────┼────────────────┤
│ aapl    │ volume    │ volume-aapl    │
└─────────┴───────────┴────────────────┘
```
