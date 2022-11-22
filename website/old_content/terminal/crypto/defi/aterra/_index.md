```
usage: aterra [--asset {ust,luna,sdt}] [--address ADDRESS] [-h] [--export {csv,json,xlsx}]
```

Displays the 30-day history of an asset in a certain terra address. [Source: <https://terra.engineer/>]

```
optional arguments:
  --asset {ust,luna,sdt}
                        Terra asset {ust,luna,sdt} Default: ust (default: ust)
  --address ADDRESS     Terra address. Valid terra addresses start with 'terra' (default: None)
  -h, --help            show this help message (default: False)
  --export {csv,json,xlsx}
                        Export raw data into csv, json, xlsx (default: )
```

Example:

```
2022 Feb 15, 06:00 (🦋) /crypto/defi/ $ aterra --asset luna --address terra18vnrzlzm2c4xfsx382pj2xndqtt00rvhu24sqe
```

![aterra](https://user-images.githubusercontent.com/46355364/154049081-7f2298ba-8a0e-4aaa-a5b1-5bc4f92af312.png)
