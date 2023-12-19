---
title: load
description: The documentation page describes the crypto currency load function in
  OpenBB's Terminal. It helps to get data for any crypto currency by specifying parameters
  such as symbol, start date, interval, exchange, vs_currency, end_date and the source
  of the data. It then returns a PD DataFrame with price and volume data.
keywords:
- cryptocurrency
- crypto load
- crypto currency data
- parameters
- CCXT
- CoinGecko
- YahooFinance
- Binance
- PD Dataframe
- interval
- exchange
- vs currency
- symbol
---

import HeadTitle from '@site/src/components/General/HeadTitle.tsx';

<HeadTitle title="crypto.load - Reference | OpenBB SDK Docs" />

Load crypto currency to get data for

Source Code: [[link](https://github.com/OpenBB-finance/OpenBBTerminal/tree/main/openbb_terminal/cryptocurrency/cryptocurrency_helpers.py#L488)]

```python
openbb.crypto.load(symbol: str, start_date: Union[datetime.datetime, str, NoneType] = None, interval: Union[str, int] = "1440", exchange: str = "binance", vs_currency: str = "usdt", end_date: Union[datetime.datetime, str, NoneType] = None, source: str = "CCXT")
```

---

## Parameters

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| symbol | str | Coin to get | None | False |
| start_date | Union[datetime, Union[str, None]] | Start date to get data from with. - datetime or string format (YYYY-MM-DD) | None | True |
| interval | Union[str, int] | The interval between data points in minutes.<br/>Choose from: 1, 15, 30, 60, 240, 1440, 10080, 43200 | 1440 | True |
| exchange | str: | The exchange to get data from. | binance | True |
| vs_currency | str | Quote Currency (Defaults to usdt) | usdt | True |
| end_date | Union[datetime, Union[str, None]] | End date to get data from with. - datetime or string format (YYYY-MM-DD) | None | True |
| source | str | The source of the data<br/>Choose from: CCXT, CoinGecko, YahooFinance | CCXT | True |


---

## Returns

| Type | Description |
| ---- | ----------- |
| pd.DataFrame | Dataframe consisting of price and volume data |
---
