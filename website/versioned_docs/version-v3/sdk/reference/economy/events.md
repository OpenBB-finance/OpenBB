---
title: events
description: OpenBB SDK Function
---

# events

Get economic calendar for countries between specified dates

Source Code: [[link](https://github.com/OpenBB-finance/OpenBBTerminal/tree/main/openbb_terminal/economy/nasdaq_model.py#L21)]

```python
openbb.economy.events(countries: Union[List[str], str] = "", start_date: Optional[str] = None, end_date: Optional[str] = None)
```

---

## Parameters

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| countries | [List[str],str] | List of countries to include in calendar.  Empty returns all |  | True |
| start_date | Optional[str] | Start date for calendar | None | True |
| end_date | Optional[str] | End date for calendar | None | True |


---

## Returns

| Type | Description |
| ---- | ----------- |
| pd.DataFrame | Economic calendar |
---

## Examples


Get todays economic calendar for the United States

```python
from openbb_terminal.sdk import openbb
calendar = openbb.economy.events("United States")
```


To get multiple countries for a given date, pass the same start and end date as well as
a list of countries

```python
calendars = openbb.economy.events(["United States","Canada"], start_date="2022-11-18", end_date="2022-11-18")
```

---

