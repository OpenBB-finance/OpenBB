---
title: Customization
sidebar_position: 4
description: This documentation page details the settings and feature flags that can be defined under the `/settings` menu.
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

<HeadTitle title="Customization - Overview - Usage | OpenBB CLI Docs" />

## Settings Menu

The `/settings` menu provides methods for customizing the look of the CLI.

| Setting        |                                                      Description |
| :-----------   | :--------------------------------------------------------------- |
| `flair`        |                                 Sets the flair emoji to be used. |
| `language`     |         Select the language for the CLI menus and commands. |
| `timezone`     |                                               Select a timezone. |
| `n_rows`       | Set the number of rows to display in the CLI's interactive tables. |
| `n_cols`       | Set the number of columns to display in the CLI's interactive tables. |
| `cls`          |                                     Clear the screen after each command.  Default state is off. |
| `exithelp`     |           Automatically print the screen after navigating back one menu.  Default state is off. |
| `interactive`  | Enable/disable interactive tables.  Disabling prints the table directly on the CLI screen. |
| `overwrite`    |               Automatically overwrite exported files with the same name.  Default state is off. |
| `promptkit`    |                                         Enable auto complete and history.  Default state is on. |
| `rcontext`     |                            Remember loaded tickers while switching menus.  Default state is on. |
| `retryload`    |                Retries misspelled commands with the load function first.  Default state is off. |
| `richpanel`    |                                           Displays a border around menus.  Default state is on. |
| `tbhint`       |                                Display usage hints in the bottom toolbar.  Default state is on. |
| `version`      |                     Displays the currently installed version number in the bottom right corner. |
