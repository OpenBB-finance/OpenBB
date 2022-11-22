---
title: FAQ
sidebar_position: 3
---

# FAQ

<details><summary>Where does the data comes from?</summary>
<p>

OpenBB does not provide any data. OpenBB is a data aggregator that connects to
multiple data providers and provides a unified API to access the data.

</p>
</details>

<details><summary>What programs do I need to allow for Windows Firewall?</summary>
<p>

Windows Firewall will need to allow the following applications through (if not already):

- BranchCache
- Hyper-V
- VcXsrv
- Windows Terminal

From the Windows Security menu, click on the Firewall & Network Protection tab, then click on "Allow an app through firewall". If the applications below are not allowed to communicate through Windows Defender Firewall, change the settings to allow.

</p>
</details>

<details><summary>In what Operating Systems can I run OpenBB SDK?</summary>
<p>

OpenBB SDK is compatible with Windows, Linux, and Mac OS. Check the
[installation guide](/sdk/getstarted/installation) and [requirements outline](/sdk/getstarted/requirements) for more details.

</p>
</details>

<details><summary>How much hard drive space is required?</summary>
<p>

An installation will use approximately 4GB of space.

</p>
</details>

<details><summary>How do I launch Jupyter Lab for use with the OpenBB SDK?</summary>
<p>

From the command line, with the environment active, and from the root of the local installation folder, enter: `jupyter lab`. A browser window will launch.

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

<details><summary>How can I get help with OpenBB SDK?</summary>
<p>

You can get help with OpenBB SDK by joining our
[Discord server](https://openbb.co/discord) or contact us in our support form
[here](https://openbb.co/support).

</p>
</details>
