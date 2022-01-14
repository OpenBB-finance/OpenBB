```
usage: ayr [--export {csv,json,xlsx}] [-h]
```

Displays the 30-day history of the Anchor Yield Reserve. An increasing yield reserve indicates that the return on collateral staked by borrowers in Anchor is greater than the yield paid to depositors. A decreasing yield reserve means yield paid to depositors is outpacing the staking returns of borrower's collateral. [Source: https://terra.engineer/]
TLDR: Shows the address that contains UST that is paid on anchor interest earn.

```
optional arguments:
  --export {csv,json,xlsx}
                        Export dataframe data to csv,json,xlsx file (default:)
  -h, --help            show this help message (default: False)
```
