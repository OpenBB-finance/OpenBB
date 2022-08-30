```
usage: cpcontracts
                   [-p {btc-bitcoin,eos-eos,eth-ethereum,xrp-xrp,bch-bitcoin-cash,xem-nem,neo-neo,xlm-stellar,etc-ethereum-classic,qtum-qtum,zec-zcash,bts-bitshares,waves-waves,nxt-nxt,act-achain,ubq-ubiq,xcp-counterparty,etp-metaverse-etp,burst-burst,omni-omni,trx-tron,bnb-binance-coin,ardr-ardor,ht-huobi-token,blvr-believer,cake-pancakeswap,fsxu-flashx-ultra,chik-chickenkebab-finance,jgn-juggernaut7492,crx-cryptex,whirl-whirl-finance,eubi-eubi-token,swam-swapmatic-token,shells-shells}]
                   [-l N] [-s {id,type,active,address}] [--descend] [--export {csv,json,xlsx}] [-h]
```

Gets all contract addresses for given platform. Provide platform id with -p/--platform parameter You can display only N number of smart contracts
with --limit parameter. You can sort data by id, type, active, address --sort parameter and also with --descend flag to sort descending. Displays: id,
type, active, address

```
optional arguments:
  -p {btc-bitcoin,eos-eos,eth-ethereum,xrp-xrp,bch-bitcoin-cash,xem-nem,neo-neo,xlm-stellar,etc-ethereum-classic,qtum-qtum,zec-zcash,bts-bitshares,waves-waves,nxt-nxt,act-achain,ubq-ubiq,xcp-counterparty,etp-metaverse-etp,burst-burst,omni-omni,trx-tron,bnb-binance-coin,ardr-ardor,ht-huobi-token,blvr-believer,cake-pancakeswap,fsxu-flashx-ultra,chik-chickenkebab-finance,jgn-juggernaut7492,crx-cryptex,whirl-whirl-finance,eubi-eubi-token,swam-swapmatic-token,shells-shells}, --platform {btc-bitcoin,eos-eos,eth-ethereum,xrp-xrp,bch-bitcoin-cash,xem-nem,neo-neo,xlm-stellar,etc-ethereum-classic,qtum-qtum,zec-zcash,bts-bitshares,waves-waves,nxt-nxt,act-achain,ubq-ubiq,xcp-counterparty,etp-metaverse-etp,burst-burst,omni-omni,trx-tron,bnb-binance-coin,ardr-ardor,ht-huobi-token,blvr-believer,cake-pancakeswap,fsxu-flashx-ultra,chik-chickenkebab-finance,jgn-juggernaut7492,crx-cryptex,whirl-whirl-finance,eubi-eubi-token,swam-swapmatic-token,shells-shells}
                        Blockchain platform like eth-ethereum (default: eth-ethereum)
  -l N, --limit N     Limit of records (default: 15)
  -s {id,type,active,address}, --sort {id,type,active,address}
                        Sort by given column (default: id)
  --descend             Flag to sort in descending order (lowest first) (default: True)
  --export {csv,json,xlsx}
                        Export dataframe data to csv,json,xlsx file (default: )
  -h, --help            show this help message (default: False)
```

Example:
```
2022 Feb 15, 08:16 (✨) /crypto/ov/ $ cpcontracts
                          Contract Addresses
┌────────────────────────────────────────────────────┬───────┬────────┐
│ id                                                 │ type  │ active │
├────────────────────────────────────────────────────┼───────┼────────┤
│ -                                                  │ ERC20 │ True   │
├────────────────────────────────────────────────────┼───────┼────────┤
│ -dogeinu                                           │ ERC20 │ True   │
├────────────────────────────────────────────────────┼───────┼────────┤
│ -exotix                                            │ ERC20 │ True   │
├────────────────────────────────────────────────────┼───────┼────────┤
│ -onlychads                                         │ ERC20 │ True   │
├────────────────────────────────────────────────────┼───────┼────────┤
│ -pcore                                             │ ERC20 │ True   │
├────────────────────────────────────────────────────┼───────┼────────┤
│ -the-ether-collection                              │ ERC20 │ True   │
├────────────────────────────────────────────────────┼───────┼────────┤
│ 0175-geely-automobile                              │ ERC20 │ True   │
├────────────────────────────────────────────────────┼───────┼────────┤
│ 0241-alibaba-health-information-technology-limited │ ERC20 │ True   │
├────────────────────────────────────────────────────┼───────┼────────┤
│ 0347-angang-steel                                  │ ERC20 │ True   │
├────────────────────────────────────────────────────┼───────┼────────┤
│ 0358-jiangxi-copper                                │ ERC20 │ True   │
├────────────────────────────────────────────────────┼───────┼────────┤
│ 0522-asm-pacific-technology-limited                │ ERC20 │ True   │
├────────────────────────────────────────────────────┼───────┼────────┤
│ 0728-china-telecom                                 │ ERC20 │ True   │
├────────────────────────────────────────────────────┼───────┼────────┤
│ 0753-air-china                                     │ ERC20 │ True   │
├────────────────────────────────────────────────────┼───────┼────────┤
│ 0857-petrochina                                    │ ERC20 │ True   │
├────────────────────────────────────────────────────┼───────┼────────┤
│ 0916-china-longyuan-power                          │ ERC20 │ True   │
└────────────────────────────────────────────────────┴───────┴────────┘
```
