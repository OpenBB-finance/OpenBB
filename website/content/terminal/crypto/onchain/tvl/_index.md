```
usage: tvl [-u USERADDRESS] [-a ADDRESSNAME] [-s SYMBOL]
           [-i INTERVAL] [-h] [--export EXPORT]
```

Total value locked (TVL) metric - Ethereum ERC20
[Source:https://docs.flipsidecrypto.com/]

useraddress OR
addressname must be provided

```
options:
  -u USERADDRESS, --useraddress USERADDRESS
                        User address we'd like to take a balance
                        reading of against the contract (e.g., 0xa5407eae9ba41422680e2e00537571bcc53efbfd) (default:
                        None)
  -a ADDRESSNAME, --addressname ADDRESSNAME
                        Address name corresponding to the user
                        address (e.g., makerdao) (default: None)
  -s SYMBOL, --symbol SYMBOL
                        Contract symbol (default: USDC)
  -i INTERVAL, --interval INTERVAL
                        Interval in months (default: 1)
  -h, --help            show this help message (default: False)
  --export EXPORT       Export raw data into csv, json, xlsx and
                        figure into png, jpg, pdf, svg (default: )
```