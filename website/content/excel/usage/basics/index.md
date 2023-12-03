---
title: Basics
sidebar_position: 1
description: Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod tempor incididunt ut labore et dolore magna aliqua. Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod tempor incididunt ut labore et dolore magna aliqua.
keywords:
- Microsoft Excel
- Add-in
- Basics
---

The add-in provides 3 types of custom functions:

1. **Last value**: returns the last value of a given symbol/field combination

    - `OBB.LAST`

    Examples:

    ```excel
    =OBB.LAST("AAPL","EBITDA")
    ```

    ```excel
    =OBB.LAST("AAPL","CEO")
    ```

---

2. **Historical data**: returns the historical values of a given symbol/field combination

    - `OBB.HIST`

    Examples:

    ```excel
    =OBB.HIST("AAPL","EBITDA")
    ```

    ```excel
    =OBB.HIST("AAPL","ROE","2020-01-01","2020-12-31")
    ```

---

3. **Library**: direct access to the OpenBB library
    - `OBB.[MENU].[SUB_MENU].[COMMAND]`

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
