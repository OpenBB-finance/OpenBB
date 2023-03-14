---
sidebar_position: 5
title: Customization
description: To adjust the lay-out and settings of the OpenBB Terminal you can access the settings menu. This menu allows you to tweak how the terminal behaves. Next to that, to enable or disable certain functionalities of the terminal you can use the featflags menu.
keywords: [settings, featflags, feature flags, lay-out, advanced, customizing, openbb terminal]
---

Since the code is open source you are able to adjust anything you like. However, to make it easy for you we have created a settings and featflags menu that include the most requested features that users like to have control over. 

## Using the Settings Menu

To adjust the lay-out and settings of the OpenBB Terminal you can access the `settings` menu. This menu allows you to tweak how the terminal behaves. 

<img width="800" alt="image" src="https://user-images.githubusercontent.com/46355364/225057498-723a0310-da28-4079-8726-214618b5d5a2.png"></img>

This menu includes the following:

- `colors` define the colors you wish to use within the OpenBB Terminal.
- `dt` adds or removes the datetime from the flair (which is next to the flair).
- `flair` allows you to change the emoji that is used.
- `lang` gives the ability to change the terminal language. At this moment, the terminal is only available in English.
- `userdata` defines the folder you wish to export data you acquire from the terminal. Use quotes for custom locations.
- `tz` allows you to change the timezone if this is incorrectly displayed for you.
- `autoscaling` automatically scales plots for you if enabled (when green).
    - if `autoscaling` is enabled:
        - `pheight` sets the percentage height of the plot (graphs) displayed (if autoscaling is enabled).
        - `pwidth` sets the percentage width of the plot (graphs) displayed (if autoscaling is enabled).
    - if `autoscaling` is disabled:
        - `height` sets the height of the plot (graphs) displayed (if autoscaling is disabled).
        - `width` sets the width of the plot (graphs) displayed (if autoscaling is disabled).
- `dpi` refers to the resolution that is used for the plot (graphs)
- `backend` allows you to change the backend that is used for the graphs
- `monitor` choose which monitors to scale the plot (graphs) to if applicable
- `source` allows you to select a different source file in which the default data sources are written down
- `tbnews` whether to include the Twitter news toolbar.

## Using the Feature Flags Menu

To enable or disable certain functionalities of the terminal you can use the `featflags` menu.

<img width="800" alt="image" src="https://user-images.githubusercontent.com/46355364/225058457-507a7d0e-48a8-47f7-afa1-6967931f2255.png"></img>

By entering one of the commands on this page you are able to turn the feature flag on or off. This menu includes the following:

- `retryload` whenever you misspell commands, try to use the `load` command with it first (default is off).
- `tab` whether to use tabulate to print DataFrames, to prettify these DataFrames (default is on).
- `cls` whether to clear the command window after each command (default is off).
- `color` whether to use colors within the terminal (default is on).
- `promptkit` whether you wish to enable autocomplete and history (default is on).
- `thoughts` whether to receive a thought of the day (default is off).
- `reporthtml` whether to open reports as HTML instead of Jupyter Notebooks (default is on).
- `exithelp` whether to automatically print the help message when you use `q` (default is off).
- `rcontext` whether to remember loaded tickers and similar while switching menus (default is on).
- `rich` whether to apply a colorful rich terminal (default is on).
- `richpanel` whether to apply a colorful rich terminal panel (default is on).
- `ion` whether to enable interactive mode of MATPLOTLIB (default is on).
- `watermark` whether to include the watermark of OpenBB Terminal in figures (default is on).
- `cmdloc` whether the location of the command is displayed in figures (default is on).
- `tbhint` whether usage hints are displayed in the bottom toolbar (default is on).
- `overwrite` whether to automatically overwrite Excel files if prompted to (default is off).