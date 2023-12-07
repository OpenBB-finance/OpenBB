---
title: Basics
sidebar_position: 1
description: This page provides an overview of the basics of the OpenBB add-in for Microsoft Excel. It covers the basic usage of the add-in and the available functions.
keywords:
- Microsoft Excel
- Add-in
- Basics
- Examples
- Functions
---

> To access the following features you need to sign-in first with your OpenBB Pro account.

The add-in provides 3 types of custom functions all starting with `OBB.`.

1. **Last value**: returns the last value of a given symbol/field combination

    - `OBB.LAST`

    Examples:

    1. Getting the last price of a stock:

        ```excel
        =OBB.LAST("AAPL";"CLOSE_PRICE")
        ```

    2. Getting the industry group of a stock:

        ```excel
        =OBB.LAST("AAPL";"INDUSTRY_GROUP")
        ```

2. **Historical data**: returns the historical values of a given symbol/field combination

    - `OBB.HIST`

    Examples:

    1. Getting the historical EBITDA:

        ```excel
        =OBB.HIST("AAPL";"EBITDA")
        ```

    2. Getting the historical Return on Equity (ROE) for a given period:

        ```excel
        =OBB.HIST("AAPL";"ROE";"2020-01-01";"2020-12-31")
        ```

    :::tip
    Dates can be specified in text format (YYYY-MM-DD) or as Excel dates from a cell or `DATE(YYYY;MM;DD)`.
    :::

3. **Library**: direct access to the OpenBB library
    - `OBB.[MENU].[SUB_MENU].[COMMAND]`

    Examples:

    1. Getting balance sheet data for a stock:

        ```excel
        =OBB.EQUITY.FUNDAMENTAL.BALANCE("AAPL")
        ```

    2. Getting the latest news for a stock:

        ```excel
        =OBB.NEWS.COMPANY("AAPL")
        ```

    3. Getting the earnings calendar:

        ```excel
        =OBB.EQUITY.CALENDAR.IPO(;;"2023-11-20")
        ```

    :::tip
    If you want to skip a parameter just use semi-colon (or comma depending on your number separator) without any value. In example iii. we are skip the first parameter (provider) and the second parameter (symbol).
    :::
