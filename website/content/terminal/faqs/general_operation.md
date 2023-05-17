---
title: General Operation
sidebar_position: 3
description: General operation and troubleshooting for the OpenBB Terminal.
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
    openbb terminal,
    developer,
    OS,
    BranchCache,
    Hyper-V,
    VcXsrv,
    code block
  ]
---

import HeadTitle from '@site/src/components/General/HeadTitle.tsx';

<HeadTitle title="General Operation - Terminal | OpenBB Docs" />

Both Windows and MacOS provide a "developer mode", and enabling it may help to overcome system-related issues.

**MacOS**: Go to the System Settings, and under the "Privacy and Security" tab, scroll to the bottom and select the option to "Allow applications downloaded from App Store and identified developers". Then, scroll up to click on, "Developer Tools", and add `Terminal.app` and `Visual Studio Code` (or the preferred code editor) to the list of applications allowed to run software locally that does not meet the system's security policy.

**Windows**: Go to the Control Panel, and under the "Privacy & Security" tab, click on, "For developers". Under this menu, turn "Developer Mode" on.

From the Windows Security menu, click on the Firewall & Network Protection tab, then click on "Allow an app through firewall". If the applications below are not allowed to communicate through Windows Defender Firewall, change the settings to allow.

- BranchCache
- Hyper-V
- VcXsrv
- Windows Terminal

<details><summary>Why does a specific menu or command not exist?</summary>

It could be that you are running an outdated version in which the menu or command is not yet available. Please check the [installation guide](https://docs.openbb.co/terminal/installation) to download the most recent release.

Do note that it is also possible that the menu or command has been deprecated. If this is oversight, please reach out to us [here](https://openbb.co/support).

</details>

<details><summary>Charts do not display on Linux/WSL or Docker installation.</summary>

Check that X-11, or similar, is installed, open, and configured. Follow the instructions pertaining to the system here: [https://docs.openbb.co/terminal/installation/docker](https://docs.openbb.co/terminal/installation/docker)

</details>

<details><summary>How do I retrieve more results than is returned by default?</summary>

Most functions will have either, `--start` and `--end` flags, or a `--limit` argument. Print the help dialogue for any command by attaching, `--help` or `-h`.

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

See the guide [here](https://docs.openbb.co/terminal/usage/guides/customizing-the-terminal#styles).  The theme can be toggled between light and dark mode, directly on the individual chart.  See the [Terminal Basics page](https://docs.openbb.co/terminal/usage/basics#charts) for more information on working with the charts.

</details>

<details><summary>Can I change the colors of the text in the Terminal?</summary>

Yes, use the `colors` command under the `/settings` menu: [https://docs.openbb.co/terminal/usage/guides/customizing-the-terminal](https://docs.openbb.co/terminal/usage/guides/customizing-the-terminal)

</details>

<details><summary>After setting the preset in the stocks screener, nothing happens.</summary>

Print the current screen again with by entering, `?`. Does the name of the selected preset display? With a preset loaded, run the screener by entering one of the commands below:

- Financial
- Ownership
- Overview
- Performance
- Technical
- Valuation

</details>

<details><summary>Forecast functions say to enter a valid data set</summary>

Because an unlimited number of data sets can be loaded into the Forecast menu, each function requires defining the specific data set to be used. Add the `-d` or `--dataset` argument to the command, along with the name of the desired data set.

```console
rnn -d SPY
```

</details>

<details><summary>How do I find stocks from India, or another country?</summary>

Use the `search` command from the `/stocks` menu.  Refer to the menu's introduction guide [here](https://docs.openbb.co/terminal/usage/intros/stocks#search).

As an example, try this:

```console
search --country india --exchange-country india --limit 1000
```

</details>
