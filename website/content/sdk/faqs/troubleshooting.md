---
title: General Troubleshooting
sidebar_position: 5
description: TBD
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
  ]
---

## General Troubleshooting

Both Windows and MacOS provide a "developer mode", and enabling it may help.

**MacOS**: Go to the System Settings, and under the "Privacy and Security" tab, scroll to the bottom and select the option to "Allow applications downloaded from App Store and identified developers". Then, scroll up to click on, "Developer Tools", and add `Terminal.app` and `Visual Studio Code` (or the preferred code editor) to the list of applications allowed to run software locally that does not meet the system's security policy.

**Windows**: Go to the Control Panel, and under the "Privacy & Security" tab, click on, "For developers". Under this menu, turn "Developer Mode" on.

From the Windows Security menu, click on the Firewall & Network Protection tab, then click on "Allow an app through firewall". If the applications below are not allowed to communicate through Windows Defender Firewall, change the settings to allow.

- BranchCache
- Hyper-V
- VcXsrv
- Windows Terminal

<details><summary>Why does a specific menu or command not exist?</summary>

It could be that you are running an outdated version in which the menu or command is not yet available. Please check the [installation guide](https://docs.openbb.co/terminal/quickstart/installation) to download the most recent release.

Do note that it is also possible that the menu or command has been deprecated. If this is oversight, please reach out to us [here](https://openbb.co/support).

</details>
