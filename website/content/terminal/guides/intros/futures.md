---
title: Futures
keywords:
  [
    "forex",
    "currency",
    "money",
    "hedge",
    "dollar",
    "euro",
    "futures",
    "future",
    "interest",
    "rates",
    "forwards",
    "commodities",
    "bonds",
    "treasuries",
  ]
excerpt: "This guide explains how to use the Futures menu and provides a brief description of its sub-menus"

---

The Futures menu provides historical prices and the current term structure for an asset. This menu is accessible from the Main menu by typing `futures` and pressing the `enter` key.

<img width="1135" alt="Futures Menu" src="https://user-images.githubusercontent.com/85772166/197641556-80d83abb-6290-4fc9-b80a-331bcc5751e5.png"/>

### How to Use

There are three basic functions within this menu Search, Historical and Curve.

`Search` allows the user to find which instruments are supported, and can be searched by the description. For example, searching for silver will return these results:

```
search -d silver
```

<img width="603" alt="Search Futures" src="https://user-images.githubusercontent.com/85772166/197641622-8e90785a-f758-4911-9068-eb4f528f42e9.png"/>

To view an entire category, attach the `--category` flag to the function and select using the arrow keys.

<img width="275" alt="Futures Categories" src="https://user-images.githubusercontent.com/85772166/197641664-3e63b68b-a4be-4dd6-a7a8-47e0cbef0b61.png"/>

```
search --category currency
```

<img width="493" alt="Currency Futures" src="https://user-images.githubusercontent.com/85772166/197641730-b488d1d0-3f82-4da4-8f07-8973b86e9585.png"/>

Both `curve` and `historical` use the ticker symbol shown by the search function, for example, to see a chart of the current Eurodollar Futures term structure, simply enter:

```
`curve GE`
```

<img width="1218" alt="Eurodollar Futures Curve" src="https://user-images.githubusercontent.com/85772166/197641789-dc56b59f-e5c3-4186-b88c-9f899cdf650a.png"/>

The raw data can be printed as a table or exported to a file, by attaching the optional arguments: `--raw`, or, `--export {filetype}`. For example, Global Emissions Offset Futures:

```
curve GEO --raw
```

<img width="386" alt="Futures Raw Data" src="https://user-images.githubusercontent.com/85772166/197641865-aa3c8649-21c2-4217-b921-f426776430b1.png"/>

The continuous chart is displayed with the `historical` command + the symbol. To see the optional arguments available for the command, deploy the `-h` flag. For example, the Eurodollar Futures contract for December 2024 expiry is displayed with:

```
historical GE -s 2015-01-01 -e 2024-12
```

<img width="1205" alt="Historical Price of GEZ24.CME" src="https://user-images.githubusercontent.com/85772166/197641999-599e2b0a-4578-4d36-b5c5-704c5ac9a0fa.png"/>

Multiple continuous charts can be plotted on the same chart by using a comma-separated list:

```
historical GE,ZQ -s 2007-01-01
```

<img width="1233" alt="Historical Price of GE=F & ZQ=F" src="https://user-images.githubusercontent.com/85772166/197642051-a5a02f15-6e5b-464f-9ba9-0d2299488021.png"/>