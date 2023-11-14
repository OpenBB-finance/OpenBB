---
title: load
description: The page provides an explanation of the 'load' feature that is used to
  load forex data for two given symbols. It includes the source code link and details
  about the parameters including to_symbol, from_symbol, resolution, interval, start_date,
  source, and verbose.
keywords:
- forex data
- currency symbols
- forex parameters
- load forex data
- forex data source
- YahooFinance forex data
- data resolution
- data interval
- verbose data loading
---

import HeadTitle from '@site/src/components/General/HeadTitle.tsx';

<HeadTitle title="forex.load - Reference | OpenBB SDK Docs" />

Load forex for two given symbols.

Source Code: [[link](https://github.com/OpenBB-finance/OpenBBTerminal/tree/main/openbb_terminal/forex/forex_helper.py#L95)]

```python
openbb.forex.load(to_symbol: str, from_symbol: str, resolution: str = "d", interval: str = "1day", start_date: Optional[str] = None, source: str = "YahooFinance", verbose: bool = False)
```

---

## Parameters

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| to_symbol | str | The from currency symbol. Ex: USD, EUR, GBP, YEN | None | False |
| from_symbol | str | The from currency symbol. Ex: USD, EUR, GBP, YEN | None | False |
| resolution | str | The resolution for the data, by default "d" | d | True |
| interval | str | What interval to get data for, by default "1day" | 1day | True |
| start_date | Optional[str] | When to begin loading in data, by default last_year.strftime("%Y-%m-%d") | None | True |
| source | str | Where to get data from, by default "YahooFinance" | YahooFinance | True |
| verbose | bool | Display verbose information on what was the pair that was loaded, by default True | False | True |


---

## Returns

| Type | Description |
| ---- | ----------- |
| pd.DataFrame | The loaded data |
---
