---
title: Configuration & Settings
sidebar_position: 5
description: This documentation page details the various settings and feature flags used to customize the OpenBB Platform CLI.
keywords:
- Settings Menu
- Feature Flags Menu
- customize CLI
- alter CLI behaviour
- environment variables
- Documentation
- OpenBB Platform CLI
- preferences
- user
---

import HeadTitle from '@site/src/components/General/HeadTitle.tsx';

<HeadTitle title="Configuration & Settings - | OpenBB Platform CLI Docs" />

In addition to the OpenBB Platform's `user_settings.json` file, described [here](/platform/user_guides/settings_and_environment_variables), there are settings and environment variables affecting the CLI only.

:::important
API credentials are defined in the `user_settings.json` file.

Find all data providers [here](/platform/user_guides/extensions), and manage all your credentials directly on the [OpenBB Hub](https://my.openbb.co/app/platform/credentials).

Define default data sources by following the pattern outlined [here](data-sources)
:::

## Settings Menu

The `/settings` menu provides methods for customizing the look and feel of the CLI. The menu is divided into two sections:

- Feature Flags
  - On/Off status is reflected by red/green text.
  - Status is toggled by entering the item as a command.
- Preferences
  - Choices and options will be presented as a typical function.

### Feature Flags

| Feature Flags  |                                                      Description |
| :-----------   | :--------------------------------------------------------------- |
| `interactive`  | Enable/disable interactive tables.  Disabling prints the table directly on the CLI screen. |
| `cls`          |                                     Clear the screen after each command.  Default state is off. |
| `promptkit`    |                                         Enable auto complete and history.  Default state is on. |
| `richpanel`    |                                           Displays a border around menus.  Default state is on. |
| `tbhint`       |                                Display usage hints in the bottom toolbar.  Default state is on. |
| `exithelp`     |           Automatically print the screen after navigating back one menu.  Default state is off. |
| `overwrite`    |               Automatically overwrite exported files with the same name.  Default state is off. |
| `obbject_msg`  |       Displays a message whenever a new result is added to the registry.  Default state is off. |
| `version`      |                     Displays the currently installed version number in the bottom right corner. |

### Preferences

| Preferences    |                                                      Description |
| :-----------   | :--------------------------------------------------------------- |
| `console_style`           | apply a custom rich style to the CLI  |
| `flair`                   | choose flair icon      |
| `timezone`                | pick timezone |
| `language`                | translation language |
| `n_rows`                  | number of rows to show on non interactive tables |
| `n_cols`                  | number of columns to show on non interactive tables |
| `obbject_res`             | define the maximum number of obbjects allowed in the registry  |
| `obbject_display`         | define the maximum number of cached results to display on the help menu  |
