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

import HeadTitle from '@site/src/components/General/HeadTitle.tsx';

<HeadTitle title="Basics | OpenBB Add-in for Excel Docs" />

The OpenBB Add-in for Excel provides direct access to the OpenBB platform, where each function implements the following pattern:

- `OBB.[MENU].[SUB_MENU].[COMMAND]`

:::tip
Use the &lt;TAB&gt; key to autocomplete the function name after typing `=OBB.`
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
   =OBB.EQUITY.CALENDAR.IPO(,"2023-11-20")
   ```

:::tip
If you want to skip a parameter use comma (or semi-colon depending on your number separator) without any value. In example iii. we are skipping the first parameter (symbol).
:::

## Advanced

<div style={{display: 'flex', justifyContent: 'center'}}>
    <iframe
        style={{width: '800px', height: '450px', display: 'block', margin: '0 auto'}}
        src="https://www.youtube.com/embed/mk-NDjH8CDE?si=oL1Iqh1yJc24dh-K"
        title="YouTube video player"
        frameBorder="0"
        allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture; web-share"
    />
</div>
