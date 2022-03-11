```
usage: govp [-l LIMIT] [-s {submitTime,id,depositEndTime,status,type,title,Yes,No}] [--status {voting,deposit,passed,rejected,all}] [--descend] [-h] [--export {csv,json,xlsx}]
```

Displays terra blockchain governance proposals list. [Source: https://fcd.terra.dev/swagger]

```
optional arguments:
  -l LIMIT, --limit LIMIT
                        Number of proposals to show (default: 10)
  -s {submitTime,id,depositEndTime,status,type,title,Yes,No}, --sort {submitTime,id,depositEndTime,status,type,title,Yes,No}
                        Sort by given column. Default: id (default: id)
  --status {voting,deposit,passed,rejected,all}
                        Status of proposal. Default: all (default: all)
  --descend             Flag to sort in descending order (lowest first) (default: False)
  -h, --help            show this help message (default: False)
  --export {csv,json,xlsx}
                        Export raw data into csv, json, xlsx (default: )
```

Example:
```
2022 Feb 15, 06:19 (✨) /crypto/defi/ $ govp
┌─────┬──────────────────┬──────────────────┬──────────┬──────────────────────┬────────────────────────────────────────┬─────┬────┬─────────┬──────────────┐
│ Id  │ Submit time      │ Deposit end time │ Status   │ Type                 │ Title                                  │ Yes │ No │ Abstain │ No with veto │
├─────┼──────────────────┼──────────────────┼──────────┼──────────────────────┼────────────────────────────────────────┼─────┼────┼─────────┼──────────────┤
│ 191 │ 2022-02-14 04:11 │ 2022-02-28 04:11 │ Deposit  │ Text Proposal        │ Whithdraw money on cash machine with   │ 0   │ 0  │ 0       │ 0            │
│     │                  │                  │          │                      │ QRcode using Terra mobile  app         │     │    │         │              │
├─────┼──────────────────┼──────────────────┼──────────┼──────────────────────┼────────────────────────────────────────┼─────┼────┼─────────┼──────────────┤
│ 190 │ 2022-02-12 09:42 │ 2022-02-26 09:42 │ Deposit  │ Text Proposal        │ test vote                              │ 0   │ 0  │ 0       │ 0            │
├─────┼──────────────────┼──────────────────┼──────────┼──────────────────────┼────────────────────────────────────────┼─────┼────┼─────────┼──────────────┤
│ 189 │ 2022-02-05 12:28 │ 2022-02-19 12:28 │ Deposit  │ Text Proposal        │ The former CEO of Ozys (TK) refuses to │ 0   │ 0  │ 0       │ 0            │
│     │                  │                  │          │                      │ join the TFL.                          │     │    │         │              │
├─────┼──────────────────┼──────────────────┼──────────┼──────────────────────┼────────────────────────────────────────┼─────┼────┼─────────┼──────────────┤
│ 188 │ 2022-02-04 00:41 │ 2022-02-18 00:41 │ Deposit  │ Text Proposal        │ Keeping an eye on the emerging market  │ 0   │ 0  │ 0       │ 0            │
├─────┼──────────────────┼──────────────────┼──────────┼──────────────────────┼────────────────────────────────────────┼─────┼────┼─────────┼──────────────┤
│ 187 │ 2022-02-03 02:13 │ 2022-02-17 02:13 │ Deposit  │ Text Proposal        │ Movement of locked values ​​between      │ 0   │ 0  │ 0       │ 0            │
│     │                  │                  │          │                      │ accounts of the same validator         │     │    │         │              │
├─────┼──────────────────┼──────────────────┼──────────┼──────────────────────┼────────────────────────────────────────┼─────┼────┼─────────┼──────────────┤
│ 186 │ 2022-02-02 01:54 │ 2022-02-16 01:54 │ Passed   │ Community-pool Spend │ 5-Yr. [REDACTED] Sports Partnership &  │ 91  │ 0  │ 0       │ 0            │
│     │                  │                  │          │                      │ Terra Community Trust (TCT) Formation  │     │    │         │              │
├─────┼──────────────────┼──────────────────┼──────────┼──────────────────────┼────────────────────────────────────────┼─────┼────┼─────────┼──────────────┤
│ 185 │ 2022-02-02 01:35 │ 2022-02-16 01:35 │ Passed   │ Parameter-change     │ Improvements to Liquidity/Minting      │ 75  │ 9  │ 12      │ 0            │
│     │                  │                  │          │                      │ Parameters                             │     │    │         │              │
├─────┼──────────────────┼──────────────────┼──────────┼──────────────────────┼────────────────────────────────────────┼─────┼────┼─────────┼──────────────┤
│ 181 │ 2022-01-31 02:00 │ 2022-02-14 02:00 │ Passed   │ Community-pool Spend │ Terra Bites v2 2022                    │ 77  │ 13 │ 5       │ 1            │
├─────┼──────────────────┼──────────────────┼──────────┼──────────────────────┼────────────────────────────────────────┼─────┼────┼─────────┼──────────────┤
│ 180 │ 2022-01-27 01:26 │ 2022-02-10 01:26 │ Passed   │ Community-pool Spend │ Onboard UST to zkSync and StarkNet     │ 97  │ 0  │ 1       │ 0            │
│     │                  │                  │          │                      │ through ZigZag Exchange                │     │    │         │              │
├─────┼──────────────────┼──────────────────┼──────────┼──────────────────────┼────────────────────────────────────────┼─────┼────┼─────────┼──────────────┤
│ 179 │ 2022-01-19 00:05 │ 2022-02-02 00:05 │ Rejected │ Parameter-change     │ Increase The Wasm Code Size            │ 80  │ 3  │ 5       │ 0            │
└─────┴──────────────────┴──────────────────┴──────────┴──────────────────────┴────────────────────────────────────────┴─────┴────┴─────────┴──────────────┘
```
