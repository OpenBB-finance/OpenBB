---
title: Help
sidebar_position: 5
description: Help for OpenBB Add-in for Excel.
keywords:
  - Microsoft Excel
  - Add-in
  - Help
---

import HeadTitle from "@site/src/components/General/HeadTitle.tsx";

<HeadTitle title="Help | Get help" />

If you face specific issues while using the add-in and the solutions provided here don't resolve them, don't hesitate to reach out to us for further assistance. You can contact us through [support@openbb.finance](mailto:support@openbb.finance).

<details>
<summary mdxType="summary">Running an OBB. function returns '#VALUE!'</summary>

- Make sure you are using the correct syntax for the function. You can find the correct syntax for each function [here](https://docs.openbb.co/excel/reference)
- If you have just opened your workbook and the OBB. function returns '#VALUE!', try recalculating the cell again - this is an ongoing issue with Excel add-ins

</details>

<details>
<summary mdxType="summary">OBB. functions are not available after installing the add-in</summary>

- Make sure OpenBB Add-in for Excel shows in the ribbon
- Go to **Insert** > **Get Add-ins** > **My Add-ins** > Click '...' when hovering OpenBB add-in > remove the add-in and install it again
- Restart your computer or manually [clear the Office cache](https://learn.microsoft.com/en-us/office/dev/add-ins/testing/clear-cache)

</details>

<details>
<summary mdxType="summary">Task pane displays "You don’t have permission to use this add-in. Contact your system administrator to request access."</summary>

- Make sure your account has the necessary permissions to use add-in
- Restart your computer or manually [clear the Office cache](https://learn.microsoft.com/en-us/office/dev/add-ins/testing/clear-cache)

</details>

<details>
<summary mdxType="summary">Editing a workbook in the browser and then on desktop app duplicates the 'OpenBB' tab in the ribbon</summary>

This is a known Excel issue. Currently, there is no definitive fix for the problem, but there are workarounds you can apply to fix the file depending on your operating system:

- **Windows**: File > Info > Inspect Workbook > Check ‘Task Pane Add-ins’ > Click ‘OK’. This will scan your workbook and remove the stale add-in reference created by Excel in the browser
- **Mac**: rename your file from .xlsx to .zip > unzip it using WinZip for Mac (don’t use the default unzip tool, otherwise it won’t work) > look for webextensions folder and delete webextension1.xml > rename the file back to .xlsx

</details>

<details>
<summary mdxType="summary">Cannot retrieve the data added to Terminal Pro through custom backend using OBB.BYOD</summary>

- Make sure your backend is running and accessible
- If you are using Mac or Safari make sure your backend is using HTTPS and has a valid SSL certificate

</details>
