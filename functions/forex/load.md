---
title: load
description: OpenBB SDK Function
---

# load

## forex_helpers.load

```python title='openbb_terminal/forex/forex_helper.py'
def load(to_symbol: str, from_symbol: str, resolution: str, interval: str, start_date: str, source: str, verbose: bool) -> DataFrame:
```
[Source Code](https://github.com/OpenBB-finance/OpenBBTerminal/tree/main/openbb_terminal/forex/forex_helper.py#L97)

Description: Load forex for two given symbols.

## Parameters

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| to_symbol | str | The from currency symbol. Ex: USD, EUR, GBP, YEN | None | False |
| from_symbol | str | The from currency symbol. Ex: USD, EUR, GBP, YEN | None | False |
| resolution | str | The resolution for the data, by default "d" | None | True |
| interval | str | What interval to get data for, by default "1day" | None | True |
| start_date | str | When to begin loading in data, by default last_year.strftime("%Y-%m-%d") | last_year.strftime | True |
| source | str | Where to get data from, by default "YahooFinance" | None | True |
| verbose | bool | Display verbose information on what was the pair that was loaded, by default True | True | True |

## Returns

| Type | Description |
| ---- | ----------- |
| pd.DataFrame | The loaded data |

## Examples

