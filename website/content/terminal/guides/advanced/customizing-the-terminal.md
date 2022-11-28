---
sidebar_position: 4
title: Customizing the Terminal
---

To adjust the lay-out and settings of the OpenBB Terminal you can access the `settings` menu. This menu allows you to
tweak how the terminal behaves. This includes the following:

- `dt` adds or removes the datetime from the flair (which is next to the emoji).
- `flair` allows you to change the emoji that is used.
- `lang` gives the ability to change the terminal language. At this moment, the terminal is only available in English.
- `export` defines the folder you wish to export data you acquire from the terminal. Use quotes for custom locations.
- `tz` allows you to change the timezone if this is incorrectly displayed for you.
- `autoscaling` automatically scales plots for you if enabled (when green).
- `pheight` sets the percentage height of the plot (graphs) displayed (if autoscaling is enabled).
- `pwidth` sets the percentage width of the plot (graphs) displayed (if autoscaling is enabled).
- `height` sets the height of the plot (graphs) displayed (if autoscaling is disabled).
- `width` sets the width of the plot (graphs) displayed (if autoscaling is disabled).
- `dpi` refers to the resolution that is used for the plot (graphs)
- `backend` allows you to change the backend that is used for the graphs
- `monitor` choose which monitors to scale the plot (graphs) to if applicable
- `source` allows you to select a different source file in which the default data sources are written down

Next to that, to enable or disable certain functionalities of the terminal you can use the `featflags` menu which
includes the following:

- `retryload` whenever you misspell commands, try to use the `load` command with it first (default is no).
- `tab` whether to use tabulate to print DataFrames, to prettify these DataFrames (default is yes).
- `cls` whether to clear the command window after each command (default is no).
- `color` whether to use colors within the terminal (default is yes).
- `promptkit` whether you wish to enable autocomplete and history (default is yes).
- `thoughts` whether to receive a thought of the day (default is no).
- `reporthtml` whether to open reports as HTML instead of Jupyter Notebooks (default is yes).
- `exithelp` whether to automatically print the help message when you use `q` (default is yes).
- `rcontext` whether to remember loaded tickers and similar while switching menus (default is yes).
- `rich` whether to apply a colorful rich terminal (default is yes).
- `richpanel` whether to apply a colorful rich terminal panel (default is yes).
- `ion` whether to enable interactive mode of MATPLOTLIB (default is yes).
- `watermark` whether to include the watermark of OpenBB Terminal in figures (default is yes).
- `cmdloc` whether the location of the command is displayed in figures (default is yes).
- `tbhint` whether usage hints are displayed in the bottom toolbar (default is yes).
