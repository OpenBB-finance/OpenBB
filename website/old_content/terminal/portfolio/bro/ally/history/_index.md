```
usage: history [-n NUM] [--export {csv,json,xlsx}] [-h]
```
Account transaction history
```
optional arguments:
  -n NUM, --num NUM     Number of recent transactions to show (default: 15)
  --export {csv,json,xlsx}
                        Export dataframe data to csv,json,xlsx file (default: )
  -h, --help            show this help message (default: False)
```
Sample Output:

```
╒══════════╤═════════════════════╤══════════╤══════════════════════════╤════════════╕
│   amount │ date                │ symbol   │ transactiontype          │   quantity │
╞══════════╪═════════════════════╪══════════╪══════════════════════════╪════════════╡
│    -6.91 │ 2021-08-16 00:00:00 │          │ Debit Interest Collected │       0.00 │
├──────────┼─────────────────────┼──────────┼──────────────────────────┼────────────┤
│     0.96 │ 2021-09-15 00:00:00 │ O        │ Cash Dividend            │       0.00 │
├──────────┼─────────────────────┼──────────┼──────────────────────────┼────────────┤
│     0.00 │ 2021-09-15 00:00:00 │ O        │ Mutual Fund Reinvestment │       0.01 │
├──────────┼─────────────────────┼──────────┼──────────────────────────┼────────────┤
│    -6.41 │ 2021-09-16 00:00:00 │          │ Debit Interest Collected │       0.00 │
╘══════════╧═════════════════════╧══════════╧══════════════════════════╧════════════╛
```
