---
title: Customization
sidebar_position: 4
description: This documentation page details the functionality of the Settings Menu
  and the Feature Flags Menu in the OpenBB Terminal. It instructs users how to customize
  the Terminal, alter its behaviour, and manipulate various environment variables.
keywords:
- Settings Menu
- Feature Flags Menu
- customize Terminal
- alter Terminal behaviour
- environment variables
- Documentation
---

import HeadTitle from '@site/src/components/General/HeadTitle.tsx';

<HeadTitle title="Customization - Overview - Usage | OpenBB Terminal Docs" />
The OpenBB Terminal contains two menus for altering the behaviour and presentation of the Terminal, Settings and Feature Flags, both of which are accessed from the main menu.



## Settings Menu

The `/settings` menu provides methods for customizing the look of the Terminal.

| Setting        |                                                      Description |
| :-----------   | :--------------------------------------------------------------- |
| `chart`        |                                          Select the chart style. |
| `colors`       |                        Sets the color scheme for Terminal fonts. |
| `dt`           |      Add or remove date and time from the Terminal command line. |
| `flair`        |                                 Sets the flair emoji to be used. |
| `height`       |                                     Set the default plot height. |
| `lang`         |         Select the language for the Terminal menus and commands. |
| `source`       | Use an alternate data sources file. (Not recommended to change.) |
| `table`        |                                          Select the table style. |
| `tz`           |                                               Select a timezone. |
| `userdata`     |              Change the local path to the OpenBBUserData folder. |
| `width`        |                                      Set the default plot width. |

### Style example

Set charts and tables styles as light or dark mode.

```console
(🦋) /settings/ $ table -s light
```

```console
(🦋) /settings/ $ chart -s dark
```

### Timezone example

Set the local timezone for the Terminal

```console
(🦋) /settings/ $ tz Africa/Johannesburg
```

## Feature Flags Menu

The `/featflags` menu provides methods for altering the behaviour and responses with environment variables. These configurations are on/off, and the status is indicated by the red/green text of each.  Each parameter is listed below.

|  Feature       |                                                                                     Description |
| :-----------   | :---------------------------------------------------------------------------------------------- |
| `cls`          |                                     Clear the screen after each command.  Default state is off. |
| `exithelp`     |           Automatically print the screen after navigating back one menu.  Default state is off. |
| `interactive`  | Enable/disable interactive tables.  Disabling prints the table directly on the Terminal screen. |
| `overwrite`    |               Automatically overwrite exported files with the same name.  Default state is off. |
| `promptkit`    |                                         Enable auto complete and history.  Default state is on. |
| `rcontext`     |                            Remember loaded tickers while switching menus.  Default state is on. |
| `retryload`    |                Retries misspelled commands with the load function first.  Default state is off. |
| `reporthtml`   |                                           Generate reports as HTML files.  Default state is on. |
| `richpanel`    |                                           Displays a border around menus.  Default state is on. |
| `tbhint`       |                                Display usage hints in the bottom toolbar.  Default state is on. |
| `version`      |                     Displays the currently installed version number in the bottom right corner. |

### Interactive example

When it is off, the Terminal displays all tables directly on the screen instead of opening a window.

```console
(🦋) /stocks/ $ quote spy

                    SPY Quote
┏━━━━━━━━━━━━━━━━━━━━━━━┳━━━━━━━━━━━━━━━━━━━━━━━━┓
┃ Info                  ┃ Value                  ┃
┡━━━━━━━━━━━━━━━━━━━━━━━╇━━━━━━━━━━━━━━━━━━━━━━━━┩
│ Symbol                │ SPY                    │
├───────────────────────┼────────────────────────┤
│ Name                  │ SPDR S&P 500 ETF Trust │
├───────────────────────┼────────────────────────┤
│ Price                 │ 412.43                 │
├───────────────────────┼────────────────────────┤
│ Changes percentage    │ 0.06                   │
├───────────────────────┼────────────────────────┤
│ Change                │ 0.23                   │
├───────────────────────┼────────────────────────┤
│ Day low               │ 410.60                 │
├───────────────────────┼────────────────────────┤
│ Day high              │ 413.06                 │
├───────────────────────┼────────────────────────┤
│ Year high             │ 431.73                 │
├───────────────────────┼────────────────────────┤
│ Year low              │ 348.11                 │
├───────────────────────┼────────────────────────┤
│ Market cap            │ 378.521 B              │
├───────────────────────┼────────────────────────┤
│ Price avg50           │ 402.47                 │
├───────────────────────┼────────────────────────┤
│ Price avg200          │ 394.88                 │
├───────────────────────┼────────────────────────┤
│ Exchange              │ AMEX                   │
├───────────────────────┼────────────────────────┤
│ Volume                │ 44.621 M               │
├───────────────────────┼────────────────────────┤
│ Avg volume            │ 89774263               │
├───────────────────────┼────────────────────────┤
│ Open                  │ 411.99                 │
├───────────────────────┼────────────────────────┤
│ Previous close        │ 412.20                 │
├───────────────────────┼────────────────────────┤
│ Eps                   │ 19.85                  │
├───────────────────────┼────────────────────────┤
│ Pe                    │ 20.78                  │
├───────────────────────┼────────────────────────┤
│ Earnings announcement │ 2017-11-29 17:00:00    │
├───────────────────────┼────────────────────────┤
│ Shares outstanding    │ 917.782 M              │
├───────────────────────┼────────────────────────┤
│ Timestamp             │ 2023-04-24 12:34:22    │
└───────────────────────┴────────────────────────┘
```

### Overwrite example

Enable this feature flag to remove the prompt when exporting a file with the same name. This will only overwrite an existing `XLSX` file if the `--sheet-name` is not defined.

### Exit help example

Enabling this prints the parent menu on the screen when going back from a sub-menu.
