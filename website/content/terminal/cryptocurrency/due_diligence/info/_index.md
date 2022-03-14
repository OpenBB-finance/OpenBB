```
usage: info [--export {csv,json,xlsx}] [-h]
```

Shows basic information about loaded coin like: Name, Symbol, Description, Market Cap, Public Interest, Supply, and Price related metrics

```
optional arguments:
  --export {csv,json,xlsx}
                        Export dataframe data to csv,json,xlsx file (default: )
  -h, --help            show this help message (default: False)
```

Example:
```
2022 Feb 15, 07:34 (✨) /crypto/dd/ $ info
                                              Basic Coin Information
┌─────────────────────────────┬──────────────────────────────────────────────────────────────────────────────────┐
│ Metric                      │ Value                                                                            │
├─────────────────────────────┼──────────────────────────────────────────────────────────────────────────────────┤
│ Id                          │ bitcoin                                                                          │
├─────────────────────────────┼──────────────────────────────────────────────────────────────────────────────────┤
│ Name                        │ Bitcoin                                                                          │
├─────────────────────────────┼──────────────────────────────────────────────────────────────────────────────────┤
│ Symbol                      │ btc                                                                              │
├─────────────────────────────┼──────────────────────────────────────────────────────────────────────────────────┤
│ Description                 │ Bitcoin is the first successful internet money based on peer-to-peer technology; │
│                             │ whereby no central bank or authority is involved in the transaction and          │
│                             │ production of the Bitcoin currency. It was created by an anonymous               │
│                             │ individual/group under the name, Satoshi Nakamoto. The source code is available  │
│                             │ publicly as an open source project, anybody can look at it and be part of the    │
│                             │ developmental process. Bitcoin is changing the way we see money as we speak. The │
│                             │ idea was to produce a means of exchange, independent of any central authority,   │
│                             │ that could be transferred electronically in a secure, verifiable and immutable   │
│                             │ way. It is a decentralized peer-to-peer internet currency making mobile payment  │
│                             │ easy, very low transaction fees, protects your identity, and it works anywhere   │
│                             │ all the time with no central authority and banks. Bitcoin is designed to have    │
│                             │ only 21 million BTC ever created, thus making it a deflationary currency.        │
│                             │ Bitcoin uses the SHA-256 hashing algorithm with an average transaction           │
│                             │ confirmation time of 10 minutes. Miners today are mining Bitcoin using ASIC chip │
│                             │ dedicated to only mining Bitcoin, and the hash rate has shot up to peta hashes.  │
│                             │ Being the first successful online cryptography currency, Bitcoin has inspired    │
│                             │ other alternative currencies such as Litecoin, Peercoin, Primecoin, and so on.   │
│                             │ The cryptocurrency then took off with the innovation of the turing-complete      │
│                             │ smart contract by Ethereum which led to the development of other amazing         │
│                             │ projects such as EOS, Tron, and even crypto-collectibles such as CryptoKitties.  │
├─────────────────────────────┼──────────────────────────────────────────────────────────────────────────────────┤
│ Contract Address            │ {}                                                                               │
├─────────────────────────────┼──────────────────────────────────────────────────────────────────────────────────┤
│ Market Cap Rank             │ 1                                                                                │
├─────────────────────────────┼──────────────────────────────────────────────────────────────────────────────────┤
│ Public Interest Score       │ 0.34                                                                             │
├─────────────────────────────┼──────────────────────────────────────────────────────────────────────────────────┤
│ Total Supply                │ 21000000.00                                                                      │
├─────────────────────────────┼──────────────────────────────────────────────────────────────────────────────────┤
│ Max Supply                  │ 21000000.00                                                                      │
├─────────────────────────────┼──────────────────────────────────────────────────────────────────────────────────┤
│ Circulating Supply          │ 18958987.00                                                                      │
├─────────────────────────────┼──────────────────────────────────────────────────────────────────────────────────┤
│ Price Change Percentage 24H │ 4.47                                                                             │
├─────────────────────────────┼──────────────────────────────────────────────────────────────────────────────────┤
│ Price Change Percentage 7D  │ 0.82                                                                             │
├─────────────────────────────┼──────────────────────────────────────────────────────────────────────────────────┤
│ Price Change Percentage 30D │ 2.41                                                                             │
├─────────────────────────────┼──────────────────────────────────────────────────────────────────────────────────┤
│ Current Price Btc           │ 1.00                                                                             │
├─────────────────────────────┼──────────────────────────────────────────────────────────────────────────────────┤
│ Current Price Eth           │ 14.27                                                                            │
├─────────────────────────────┼──────────────────────────────────────────────────────────────────────────────────┤
│ Current Price Usd           │ 44269                                                                            │
└─────────────────────────────┴──────────────────────────────────────────────────────────────────────────────────┘
```
