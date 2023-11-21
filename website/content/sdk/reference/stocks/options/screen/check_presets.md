---
title: check_presets
description: This page explains the check_presets function used in option screener
  to check the preset values. The function takes a dictionary with presets from configparser
  as argument and returns a string of accumulated errors.
keywords:
- check_presets
- Option Screener
- Preset values
- openbb.stocks.options.screen
- configparser
- Error accumulation
---

import HeadTitle from '@site/src/components/General/HeadTitle.tsx';

<HeadTitle title="stocks.options.screen.check_presets - Reference | OpenBB SDK Docs" />

Checks option screener preset values

Source Code: [[link](https://github.com/OpenBB-finance/OpenBBTerminal/tree/main/openbb_terminal/stocks/options/screen/syncretism_model.py#L251)]

```python
openbb.stocks.options.screen.check_presets(preset_dict: dict)
```

---

## Parameters

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| preset_dict | dict | Defined presets from configparser | None | False |


---

## Returns

| Type | Description |
| ---- | ----------- |
| str | String of all errors accumulated |
---
