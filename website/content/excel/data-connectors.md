---
title: Data connectors
sidebar_position: 4
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

OpenBB Add-In for Excel allows you to access your [data connectors](https://docs.openbb.co/pro/main-menu/data-connectors) from OpenBB Terminal Pro inside Microsoft Excel.

To access data from a [single widget](https://docs.openbb.co/pro/main-menu/data-connectors/single-widget) use:

```excel
=OBB.BYOD("widget_name")
```

To access data from your own [backend](https://docs.openbb.co/pro/main-menu/data-connectors/integrate-your-own-backend) use:

```excel
=OBB.BYOD("widget_name","backend_name")
```

#### Additional notes

- Make sure your backend's CORS settings allow requests coming from <https://excel.openbb.co>.
- Requests via HTTP will be blocked by Excel. So if you are using the Add-in for Excel on Mac or Office on the web with Safari browser you need to run your backend via HTTPS.
