---
title: Data connectors
sidebar_position: 3
description: Access your data connectors from OpenBB Terminal Pro inside OpenBB Add-in for Excel.
keywords:
  - Microsoft Excel
  - Add-in
  - Advanced
  - Data connectors
  - BYOD
  - Bring your own data
---

<!-- markdownlint-disable MD033 -->

import HeadTitle from '@site/src/components/General/HeadTitle.tsx';

<HeadTitle title="Data connectors | OpenBB Add-in for Excel Docs" />

OpenBB Add-In for Excel allows you to access your [data connectors](https://docs.openbb.co/pro/data-connectors) from OpenBB Terminal Pro inside Microsoft Excel. This can be done using the [OBB.BYOD](https://docs.openbb.co/excel/reference/byod) function.

## [Single widget](https://docs.openbb.co/pro/data-connectors/single-widget)

```excel
=OBB.BYOD("widget_name")
```

:::info

- Make sure your widget is setup in the OpenBB Terminal Pro.

:::

## [Own backend](https://docs.openbb.co/pro/data-connectors/integrate-your-own-backend)

```excel
=OBB.BYOD("widget_name","backend_name")
```

If your backend supports it is possible to pass a symbol, a date or other optional parameters:

```excel
=OBB.BYOD("widget_name","backend_name","my_symbol","YYYY-MM-DD",{"param1":"value1","param2":"value2", ...})
```

:::tip
The easiest way to pass optional parameters is to write them into cells and reference them in the function. For example, `=OBB.BYOD(...,A1:B2)` where A1 contains "param1", B1 "value1", A2 "param2", B2 "value2" and so on.
:::

:::info

- Make sure your backend's CORS settings allow requests coming from [https://excel.openbb.co](https://excel.openbb.co).
- Requests via HTTP will be blocked by Excel. So if you are using the Add-in for Excel on Mac or Office on the web with Safari browser you need to run your backend via HTTPS.

:::

## [Native integrations](https://docs.openbb.co/pro/data-connectors#native-integrations)

Supported native integrations:

- database
- snowflake

```excel
=OBB.BYOD("widget_name","native_integration")
```

:::info

- Make sure your OpenBB Data Connector is properly configured and the widget is setup in the OpenBB Terminal Pro.
- Native integrations are available only for Excel on the web or Windows.

:::
