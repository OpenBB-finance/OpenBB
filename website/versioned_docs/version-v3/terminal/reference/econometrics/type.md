---
title: type
description: OpenBB Terminal Function
---

# type

Show the type of the columns of the dataset and/or change the type of the column

### Usage

```python
type [-n {}] [--format {int,float,str,bool,category,date}]
```

---

## Parameters

| Name | Description | Default | Optional | Choices |
| ---- | ----------- | ------- | -------- | ------- |
| name | Provide dataset.column series to change type or dataset to see types. | None | True | None |
| format | Set the format for the dataset.column defined. This can be: date, int, float, str, bool or category | None | True | int, float, str, bool, category, date |


---

## Examples

```python
txt
2022 Feb 28, 15:53 (🦋) /econometrics/ $ load wage_panel -a wp

2022 Feb 28, 15:53 (🦋) /econometrics/ $ type
           wp
┏━━━━━━━━━━━━┳━━━━━━━━━┓
┃ column     ┃ dtype   ┃
┡━━━━━━━━━━━━╇━━━━━━━━━┩
│ nr         │ int64   │
├────────────┼─────────┤
│ year       │ int64   │
├────────────┼─────────┤
│ black      │ int64   │
├────────────┼─────────┤
│ exper      │ int64   │
├────────────┼─────────┤
│ hisp       │ int64   │
├────────────┼─────────┤
│ hours      │ int64   │
├────────────┼─────────┤
│ married    │ int64   │
├────────────┼─────────┤
│ educ       │ int64   │
├────────────┼─────────┤
│ union      │ int64   │
├────────────┼─────────┤
│ lwage      │ float64 │
├────────────┼─────────┤
│ expersq    │ int64   │
├────────────┼─────────┤
│ occupation │ int64   │
└────────────┴─────────┘
```
---
