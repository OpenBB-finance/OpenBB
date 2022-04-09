```
usage: newsletter [-l LIMIT] [-h] [--export {csv,json,xlsx}]
```

Display DeFi related substack newsletters. [Source: substack.com]

```
optional arguments:
  -l LIMIT, --limit LIMIT
                        Number of records to display (default: 10)
  -h, --help            show this help message (default: False)
  --export {csv,json,xlsx}
                        Export raw data into csv, json, xlsx (default: )
```

Example:
```
2022 Feb 15, 06:26 (✨) /crypto/defi/ $ newsletter
                                                                Substack Newsletters
┌───────────────────────────────────────────────────┬─────────────────────┬─────────────────────────────────────────────────────────────────────────┐
│ Title                                             │ Date                │ Link                                                                    │
├───────────────────────────────────────────────────┼─────────────────────┼─────────────────────────────────────────────────────────────────────────┤
│ DEBRIEF - Crypto in Washington | Congressman Tom  │ 2022-02-14 11:30:49 │ https://shows.banklesshq.com/p/debrief-crypto-in-washington-congressman │
│ Emmer                                             │                     │                                                                         │
├───────────────────────────────────────────────────┼─────────────────────┼─────────────────────────────────────────────────────────────────────────┤
│  105 - Crypto in Washington | Congressman Tom     │ 2022-02-14 11:30:48 │ https://shows.banklesshq.com/p/-105-crypto-in-washington-congressman    │
│ Emmer                                             │                     │                                                                         │
├───────────────────────────────────────────────────┼─────────────────────┼─────────────────────────────────────────────────────────────────────────┤
│ EARLY ACCESS - Crypto in Washington | Congressman │ 2022-02-11 23:14:23 │ https://shows.banklesshq.com/p/early-access-crypto-in-washington        │
│ Tom Emmer                                         │                     │                                                                         │
├───────────────────────────────────────────────────┼─────────────────────┼─────────────────────────────────────────────────────────────────────────┤
│  ROLLUP: Bitfinex Hack | Super Crypto Bowl | Aave │ 2022-02-11 13:23:29 │ https://shows.banklesshq.com/p/-rollup-bitfinex-hack-super-crypto       │
│ Social Network | Vitalik Supports Assange DAO11   │                     │                                                                         │
├───────────────────────────────────────────────────┼─────────────────────┼─────────────────────────────────────────────────────────────────────────┤
│ Syscoin Ecosystem Update: Pegasys DEX Launch      │ 2022-01-28 18:59:03 │ https://defislate.substack.com/p/syscoin-ecosystem-update-pegasys       │
└───────────────────────────────────────────────────┴─────────────────────┴─────────────────────────────────────────────────────────────────────────┘
```
