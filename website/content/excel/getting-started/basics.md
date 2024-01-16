---
title: Basics
sidebar_position: 2
description: This page provides an overview of the basics of the OpenBB add-in for Microsoft Excel. It covers the basic usage of the add-in and the available functions.
keywords:
- Microsoft Excel
- Add-in
- Basics
- Examples
- Functions
---

The OpenBB Excel Add-in provides direct access to the OpenBB platform, where each function implements the following pattern:

- `OBB.[MENU].[SUB_MENU].[COMMAND]`

:::tip
Use the <TAB\> key to autocomplete the function name after typing `=OBB.`
:::

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
    =OBB.EQUITY.CALENDAR.IPO(;"2023-11-20")
    ```

:::tip
If you want to skip a parameter use semi-colon (or comma depending on your number separator) without any value. In example iii. we are skipping the first parameter (symbol).
:::
