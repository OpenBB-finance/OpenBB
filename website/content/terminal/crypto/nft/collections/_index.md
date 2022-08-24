```
usage: collections [-l LIMIT] [-h] [--export {csv,json,xlsx}]
```

Display top ethereum collections [Source: https://nftpricefloor.com/]

```
optional arguments:
  -l LIMIT              number of collections to show (default: 5)
  -h, --help            show this help message (default: False)
  --export {csv,json,xlsx}
                        Export raw data into csv, json, xlsx (default: )
```

Example:

```
                                              NFT Collections
┏━━━━━━━━━━━━━━━━━━━━━━━┳━━━━━━━━━━━━━━━━━━━━━━━━━┳━━━━━━━━━━━━━━━┳━━━━━━━━━━━━━┳━━━━━━━━━━━━━┳━━━━━━━━━━━━┓
┃ slug                  ┃ name                    ┃ floorPriceETH ┃ totalSupply ┃ countOnSale ┃ blockchain ┃
┡━━━━━━━━━━━━━━━━━━━━━━━╇━━━━━━━━━━━━━━━━━━━━━━━━━╇━━━━━━━━━━━━━━━╇━━━━━━━━━━━━━╇━━━━━━━━━━━━━╇━━━━━━━━━━━━┩
│ cryptopunks           │ CryptoPunks             │ 67.95         │ 10000       │ 1145        │ ethereum   │
├───────────────────────┼─────────────────────────┼───────────────┼─────────────┼─────────────┼────────────┤
│ bored-ape-yacht-club  │ Bored Ape Yacht Club    │ 65.68         │ 10000       │ 775         │ ethereum   │
├───────────────────────┼─────────────────────────┼───────────────┼─────────────┼─────────────┼────────────┤
│ mutant-ape-yacht-club │ Mutant Ape Yacht Club   │ 11.99         │ 19423       │ 1075        │ ethereum   │
├───────────────────────┼─────────────────────────┼───────────────┼─────────────┼─────────────┼────────────┤
│ otherdeed             │ Otherdeed for Otherside │ 1.57          │ 100000      │ 3932        │ ethereum   │
├───────────────────────┼─────────────────────────┼───────────────┼─────────────┼─────────────┼────────────┤
│ proof-moonbirds       │ Moonbirds               │ 13.25         │ 10000       │ 145         │ ethereum   │
└───────────────────────┴─────────────────────────┴───────────────┴─────────────┴─────────────┴────────────┘
```

Example with `--fp`:

![collections fp command](https://user-images.githubusercontent.com/40023817/186201697-ff15dd9c-3b09-4c3a-b498-e98a876f1338.png)
