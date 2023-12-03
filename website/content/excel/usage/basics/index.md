---
title: Basics
sidebar_position: 1
description: Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod tempor incididunt ut labore et dolore magna aliqua. Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod tempor incididunt ut labore et dolore magna aliqua.
keywords:
- Microsoft Excel
- Add-in
- Basics
---

The add-in provides 2 types of custom functions:

1. **Last value**
    - `OBB.LAST` - Returns the last value of a given symbol/field combination.

    Example:

    ```excel
    =OBB.LAST("AAPL","EBITDA")
    ```

2. **Historical data**
    - `OBB.HIST` - Returns the historical values of a range.

    Example:

    ```excel
    =OBB.HIST("AAPL","EBITDA","2020-01-01","2020-12-31")
    ```

3. **Library**
    - `OBB.[MENU].[SUB_MENU].[COMMAND]` - Provides direct access to the OpenBB library.

    Examples:

    1. Getting balance sheet data for a stock:

        ```excel
        =OBB.EQUITY.FUNDAMENTAL.BALANCE("AAPL")
        ```

    2. Getting the earnings calendar:

        ```excel
        =OBB.EQUITY.CALENDAR.EARNINGS()
        ```

    3. Getting the latest news for a stock:

        ```excel
        =OBB.NEWS.COMPANY("AAPL")
        ```
