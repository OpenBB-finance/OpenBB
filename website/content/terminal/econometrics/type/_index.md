```
usage: type -n {} -f {int,float,str,bool,category,date} [-h]
```

Show the type of the columns of the dataset and/or change the type of the column

```
optional arguments:
  -n {}, --name {}
                        Provide dataset.column series to change type. (default: None)
  -f {int,float,str,bool,category,date}, --format {int,float,str,bool,category,date}
                        Set the format for the dataset.column defined. This can be: date, int, float, str, bool or category (default: None)
  -h, --help            show this help message (default: False)
```

Example:
```
2022 Feb 28, 15:53 (✨) /econometrics/ $ load wage_panel -a wp

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
2022 Feb 28, 15:54 (✨) /econometrics/ $ type wp.year -f category
Update 'wp.year' dataset with type 'category'

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
