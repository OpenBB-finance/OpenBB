---
title: FAQ
sidebar_position: 3
---
<details><summary>Where does the data from the OpenBB Terminal come from?</summary>
<p>

The OpenBB platform does not provide any data itself as the platform is a data aggregator that connects to
almost a hundred different data providers and APIs to access the data.

</p>
</details>

<details><summary>What programs need to be allowed for Windows Firewall?</summary>
<p>

When issues arise regarding Windows Firewall, please allow the following applications through (if not already):

- BranchCache
- Hyper-V
- VcXsrv
- Windows Terminal

From the Windows Security menu, click on the Firewall & Network Protection tab, then click on "Allow an app through firewall". If the applications below are not allowed to communicate through Windows Defender Firewall, change the settings to allow.

</p>
</details>

<details><summary>On what Operating Systems can I run the OpenBB Terminal?</summary>
<p>

The OpenBB Terminal is compatible with Windows, Mac Os and Linux. Check the
[installation guide](/terminal/quickstart/installation) and [requirements outline](/terminal/quickstart/requirements) for more details.

</p>
</details>

<details><summary>How much hard drive space is required?</summary>
<p>

An installation will use approximately 2GB of space.

</p>
</details>

<details><summary>Why is data from today missing when I use the load function?</summary>
<p>

By default, the load function requests end-of-day daily data and is not included until the EOD summary has been published. The current day's data is considered intraday and is loaded when the `interval` argument is present.

</p>
</details>

<details><summary>How do I report a bug?</summary>
<p>

First, search the open issues for another report. If one already exists, attach any relevant information and screenshots as a comment. If one does not exist, start one with this [link](https://github.com/OpenBB-finance/OpenBBTerminal/issues/new?assignees=&labels=type%3Abug&template=bug_report.md&title=%5BBug%5D)

</p>
</details>

<details><summary>How can I get help with OpenBB Terminal?</summary>
<p>

You can get help with OpenBB SDK by joining our [Discord server](https://openbb.co/discord) or contact us in our support form [here](https://openbb.co/support).

</p>
</details>
