---
title: General Operation
sidebar_position: 3
description: General operation and troubleshooting for the OpenBB SDK.
keywords:
  [
    installation,
    installer,
    install,
    guide,
    mac,
    windows,
    linux,
    python,
    github,
    macos,
    how to,
    explanation,
    openbb sdk,
    developer,
    OS,
    BranchCache,
    Hyper-V,
    VcXsrv,
    code block
  ]
---

import HeadTitle from '@site/src/components/General/HeadTitle.tsx';

<HeadTitle title="General Operation - SDK | OpenBB Docs" />

Both Windows and MacOS provide a "developer mode", and enabling it may help to overcome system-related issues.

**MacOS**: Go to the System Settings, and under the "Privacy and Security" tab, scroll to the bottom and select the option to "Allow applications downloaded from App Store and identified developers". Then, scroll up to click on, "Developer Tools", and add `Terminal.app` and `Visual Studio Code` (or the preferred code editor) to the list of applications allowed to run software locally that does not meet the system's security policy.

**Windows**: Go to the Control Panel, and under the "Privacy & Security" tab, click on, "For developers". Under this menu, turn "Developer Mode" on.

From the Windows Security menu, click on the Firewall & Network Protection tab, then click on "Allow an app through firewall". If the applications below are not allowed to communicate through Windows Defender Firewall, change the settings to allow.

- BranchCache
- Hyper-V
- VcXsrv
- Windows Terminal

<details><summary>An example code block does not work.</summary>

We try to keep example code up-to-date, but sometimes a specific example is left behind. Please submit a bug report and so that we are aware of the issue. Submit a bug report [here](https://openbb.co/support)

</details>

<details><summary>Why does a specific menu or command not exist?</summary>

It could be that you are running an outdated version in which the menu or command is not yet available. Please check the [installation guide](https://my.openbb.co/app/sdk/installation) to download the most recent release.

Do note that it is also possible that the menu or command has been deprecated. If this is oversight, please reach out to us [here](https://openbb.co/support).

</details>

<details><summary>What is the correct format for entering dates to function variables?</summary>

Dates should be entered as a string variable, inside of quotation marks, formatted as `%Y-%m-%d` - YYYY-MM-DD.

</details>

<details><summary>Does the portfolio menu allow for dividends, interest, or other distributions?</summary>

Currently, this is only possible by manually updating the portfolio file.

</details>

<details><summary>Why does my Portfolio file fail to load?</summary>

This can be the result of a formatting error, check the file in a simple text editor to observe any abnormalities in the formatting; or, it could be a bug - check the [GitHub issues page](https://github.com/OpenBB-finance/OpenBBTerminal/issues) for similar errors.

- Check that all the necessary column titles are present.
- Inspect the file to see if cells left blank have been filled unintentionally with 0 or NaN values.
- A particular asset may not be able to load data. Check for valid historical data from the Stocks menu.
- Format ticker symbols according to yFinance naming convention.
- All dates must be entered as YYYY-MM-DD.
- Transactions dated for today will fail to load historical data.
- MacOS users should attempt to avoid using the Numbers application as it has a habit of changing the formatting while saving.

Files can be formatted as either `.csv` or `.xlsx` files, and the required column headers are:

`[Date,Type,Ticker,Side,Price,Quantity,Fees,Investment,Currency,Sector,Industry,Country,Region]`

See the guide [here](https://docs.openbb.co/sdk/guides/intros/portfolio) for more information.

</details>

<details><summary>How do I change the chart styles?</summary>

Place style sheets in this folder: `OpenBBUserData/styles/user`

To select the light themes:

```python
from openbb_terminal.sdk import TerminalStyle
theme = TerminalStyle("light", "light", "light")
```

To select the dark themes:

```python
from openbb_terminal.sdk import TerminalStyle
theme = TerminalStyle("dark", "dark", "dark")
```

</details>

<details><summary>Where are the included stock screener presets located?</summary>

The files are located in the folder with the code, under:

`~/openbb_terminal/miscellaneous/stocks/screener`

Alternatively, the source code on GitHub is [here](https://github.com/OpenBB-finance/OpenBBTerminal/tree/develop/openbb_terminal/miscellaneous/stocks/screener)

</details>
