```
usage: type [-n NAME NAME] [-d {Y,m,d,m-d,Y-m,Y-d,Y-m-d,Y-d-m,default}] [-h]
```

Show the type of the columns of the dataset and/or change the type of the column

```
optional arguments:
  -n NAME NAME, --name NAME NAME
                        The first argument is the column and name of the dataset (format: <column-dataset>). The second argument is the preferred type. This can be: int, float, str, bool, date, category (default: None)
  -d {Y,m,d,m-d,Y-m,Y-d,Y-m-d,Y-d-m,default}, --dateformat {Y,m,d,m-d,Y-m,Y-d,Y-m-d,Y-d-m,default}
                        Set the format of the date. This can be: 'Y', 'M', 'D', 'm-d', 'Y-m', 'Y-d','Y-m-d', 'Y-d-m' (default: default)
  -h, --help            show this help message (default: False)

```

Example:
```
2022 Feb 28, 15:53 (✨) /econometrics/ $ load wage_panel wp

2022 Feb 28, 15:53 (✨) /econometrics/ $ type
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
```
2022 Feb 28, 15:54 (✨) /econometrics/ $ type year-wp category

2022 Feb 28, 15:55 (✨) /econometrics/ $ type
           wp            
┏━━━━━━━━━━━━┳━━━━━━━━━━┓
┃ column     ┃ dtype    ┃
┡━━━━━━━━━━━━╇━━━━━━━━━━┩
│ nr         │ int64    │
├────────────┼──────────┤
│ year       │ category │
├────────────┼──────────┤
│ black      │ int64    │
├────────────┼──────────┤
│ exper      │ int64    │
├────────────┼──────────┤
│ hisp       │ int64    │
├────────────┼──────────┤
│ hours      │ int64    │
├────────────┼──────────┤
│ married    │ int64    │
├────────────┼──────────┤
│ educ       │ int64    │
├────────────┼──────────┤
│ union      │ int64    │
├────────────┼──────────┤
│ lwage      │ float64  │
├────────────┼──────────┤
│ expersq    │ int64    │
├────────────┼──────────┤
│ occupation │ int64    │
└────────────┴──────────┘
```
