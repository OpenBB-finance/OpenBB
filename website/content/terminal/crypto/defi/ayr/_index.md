```
usage: ayr [-h] [--export {csv,json,xlsx}]
```

Displays the 30-day history of the Anchor Yield Reserve. An increasing yield reserve indicates that the return on collateral staked by borrowers in Anchor is greater than the yield paid to depositors. A decreasing yield reserve means yield paid to depositors is outpacing the staking returns of borrower's collateral. TLDR: Shows the address that contains UST that is paid on anchor interest earn. [Source: https://terra.engineer/]

```
optional arguments:
  -h, --help            show this help message (default: False)
  --export {csv,json,xlsx}
                        Export raw data into csv, json, xlsx (default: )
```

![ayr](https://user-images.githubusercontent.com/46355364/154049600-71d940f6-c7f3-4c50-a939-f76e539ed5cf.png)
