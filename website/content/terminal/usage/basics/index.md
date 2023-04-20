---
title: Basics
description: The OpenBB Terminal is a Command Line Interface (CLI) application.  Functions (commands) are called through the keyboard with results returning as charts, tables, or text.
keywords: [basics, commands, functions, features, menus, introduction, openbb terminal, obb, usage, how to, charts, tables, themes, styles, functions, data, sources, getting started]
---
## Overview

The OpenBB Terminal is a Command Line Interface (CLI) application.  Functions (commands) are called through the keyboard with results returning as charts, tables, or text.  Charts and tables are displayed in a new window, and are fully interactive, while text prints directly to the Terminal screen.  The commands are grouped into menus, with a menu or sub-menu being visually distinguishable from a function by the, `>`, on the far left of the screen.  The color of the text can be altered under the [`/settings` menu](https://docs.openbb.co/terminal/usage/guides/customizing-the-terminal).  Navigating through the Terminal menus is similar to traversing folders from any operating system's command line prompt.  Instead of `C:\Users\OpenBB\Documents`, it is, [`/stocks/options`](https://docs.openbb.co/terminal/usage/intros/stocks/options). Instead of, `cd ..`, two periods - `..` - returns to the menu one level back towards the home screen.  Absolute paths are also valid to-and-from any point.  From the [`/stocks/options`](https://docs.openbb.co/terminal/usage/intros/stocks/options) menu, go directly to [`/crypto`](https://docs.openbb.co/terminal/usage/intros/crypto).  By itself, `/`, returns to the home level.

![The Home Screen](home.png)

## Auto Complete

The OpenBB Terminal is equipped with an auto completion engine that presents choices based on the current location.  It is activated immediately upon entering any key, and where the function contains optional arguments, pressing the `space bar` after typing the command will present the list of available arguments.  This functionality dramatically reduces the number of key strokes required to perform tasks and, in many cases, eliminates the need to consult the help dialogue for reminders.  The list of choices is browsable via the up and down arrow keys.

![Auto Complete](autocomplete.png)

## Help Dialogues

### -h or --help

A help dialogue for any function at the current location is printed to the screen by attaching `-h` to the command.  The information returned contains a short description of the function and all accepted arguments.  If the parameters of an argument is a defined set of choices, they will also be included here.  For an example, the `/news` function:

```console
news -h
```

```console
usage: news [-t TERM [TERM ...]] [-s SOURCES] [-h] [--export EXPORT] [--sheet-name SHEET_NAME [SHEET_NAME ...]] [-l LIMIT]

display news articles based on term and data sources

options:
  -t TERM [TERM ...], --term TERM [TERM ...]
                        search for a term on the news
  -s SOURCES, --sources SOURCES
                        sources from where to get news from (separated by comma)
  -h, --help            show this help message
  --export EXPORT       Export raw data into csv, json, xlsx
  --sheet-name SHEET_NAME [SHEET_NAME ...]
                        Name of excel sheet to save data to. Only valid for .xlsx files.
  -l LIMIT, --limit LIMIT
                        Number of entries to show in data.

For more information and examples, use 'about news' to access the related guide.
```

### About

`about` is a global function that opens a browser to the OpenBB documentation pages at the specific command or menu.

```console
/about stocks
```

The command above will open a browser to, [Introduction to the Stocks menu](https://docs.openbb.co/terminal/usage/intros/stocks).

## Menus

### The Main Menu

The main menu, or the home screen, contains both menus and commands.  Some of these commands are global, meaning they can be called from any location within the OpenBB Terminal.  Refer to the in-depth introduction guides for each menu, for example, [Forecast](https://docs.openbb.co/terminal/usage/intros/forecast)

| Function Key |   Type   | Is Global? |                                                                     Description |
| :----------- | :------: | :--------: | ------------------------------------------------------------------------------: |
| about        | Function |    Yes    |        Opens a browser page to the documentation pages at the function or menu. |
| account      |   Menu   |     -     |                                                     Manage your OpenBB account. |
| alternative  |   Menu   |     -     |                                                          Alternative data sets. |
| crypto       |   Menu   |     -     |                                                                 Digital assets. |
| econometrics |   Menu   |     -     |                                              Econometrics and custom data sets. |
| economy      |   Menu   |     -     |                                                              The broad economy. |
| etf          |   Menu   |     -     |                                                          Exchange-Traded Funds. |
| exe          | Function |     No     |                                                 Execute OpenBB Routine Scripts. |
| featflags    |   Menu   |     -     |                                             Enable/disable Terminal behaviours. |
| fixedincome  |   Menu   |     -     |                              Central Bank and corporate bond rates and indexes. |
| forecast     |   Menu   |     -     |                                   Time series forecasting and machine learning. |
| forex        |   Menu   |     -     |                                                                 Currency pairs. |
| funds        |   Menu   |     -     |                                                                   Mutual funds. |
| futures      |   Menu   |     -     |                                                Commodity and financial futures. |
| keys         |   Menu   |     -     |                                         Set and test API keys for data sources. |
| intro        | Function |     No     |                                                    An in-Terminal introduction. |
| news         | Function |     No     |                                          Find news articles by term and source. |
| portfolio    |   Menu   |     -     |                                                    Portfolio and risk analysis. |
| record       | Function |    Yes    |                                      Starts recording an OpenBB Routine Script. |
| settings     |   Menu   |     -     |                                                       Adjust Terminal settings. |
| sources      |   Menu   |     -     |                                                  Set preferred default sources. |
| stop         | Function |    Yes    | Stop recording the OpenBB Routine Script and save to the OpenBBUserData folder. |
| support      | Function |    Yes    |                            Report a bug or create a support ticket with OpenBB. |
| survey       | Function |     No     |                                    Take a short user survey to help us improve. |
| update       | Function |     No     |   Attempt to update (**Only for Github cloned repository installations**) |
| wiki         | Function |    Yes    |                                   Query the Wikipedia API for a term or phrase. |

### Additional Global Commands

The commands listed below are not displayed on a Terminal menu, but are active globally.

| Function Key |                                       Description |
| :----------- | ------------------------------------------------: |
| cls          |                       Clears the Terminal screen. |
| exit         |                               Quits the Terminal. |
| help, h, ?   |                   Prints the current menu screen. |
| quit, q, ..  |             Navigates back one menu towards Home. |
| reset, r     | Resets the Terminal, opening to the current menu. |

## Data

Many functions will require obtaining (free or subscription) API keys from various data providers.  OpenBB provides methods for consuming these data feeds but has no control over the quality or quantity of data provided to an end-user.   None are required to get started using the Terminal.  See the list of data providers [here](https://docs.openbb.co/terminal/usage/guides/api-keys), along with instructions for entering the credentials into the OpenBB Terminal.  [Request a feature](https://openbb.co/request-a-feature) to let us know what we are missing!

### Default Data Sources

The default data source for each function (where multiple sources are available) can be defined within the [`/sources` menu](https://docs.openbb.co/terminal/usage/guides/changing-sources).  The available sources for each function are displayed on the right of the menu, and they can be distinguished by the square brackets and distinct font color group.  Unless a preference for a particular function is defined, the command will prioritize in the order they are displayed, from left-to-right, on the Terminal screen.  To override a preference or default source, select one of the other choices by attaching the, `--source`, argument to the command syntax.  The available sources for the feature will be populated by auto complete when the `space bar` is pressed after typing `--source`.  This information is also printed with the `--help` dialogue of a command.

### Importing and Exporting Data

Most functions provide a method for exporting the raw data as a CSV, JSON, or XLSX file.  Exported data and user-supplied files to import are saved to the [OpenBBUserData folder](https://docs.openbb.co/terminal/usage/guides/data).  The folder is located at the root of the operating system's User Account folder.  Follow the link for a detailed description.

## Charts

The OpenBB charting library has themes for light and dark mode.

### Light and Dark Mode

Set the theme, globally, as either light or dark.

Dark mode:

```console
/settings/chart -s dark
```

Light mode:

```console
/settings/chart -s light
```

The default state is dark mode.

```console
/stocks/load aapl -w/candle
```

![Apple Weekly Chart](chart1.png)

### Toolbar

The toolbar is located at the bottom of the window, and provides methods for:

- Panning and zooming.
- Modifying the title and axis labels.
- Adjusting the hover read out.
- Toggling light/dark mode.
- Annotating and drawing.
- Exporting raw data.
- Saving the chart as an image.
- Adding supplementary external data as an overlay.

The label for each tool is displayed by holding the mouse over it.

![Chart Tools](chart2.png)

Toggle the toolbar's visibility via the keyboard with, `ctrl + h`.

### Text Tools

Annotate a chart by clicking on the `Add Text` button, or with the keyboard, `ctrl + t`.

![Annotate Charts](chart3.png)

Enter some text, make any adjustments to the options, then `submit`.  Place the crosshairs over the desired data point and click to place the text.

![Place Text](chart4.png)

After placement, the text can be updated or deleted by clicking on it again.

![Delete Annotation](chart5.png)

The title of the chart is edited by clicking the button, `Change Titles`, near the middle center of the toolbar, immediately to the right of the `Add Text` button.

### Draw Tools

The fourth group of icons on the toolbar are for drawing lines and shapes.

- Edit the colors.
- Draw a straight line.
- Draw a freeform line.
- Draw a circle.
- Draw a rectangle.
- Erase a shape.

To draw on the chart, select one of the four drawing buttons and drag the mouse over the desired area.  Click on any existing shape to modify it by dragging with the mouse and editing the color, or remove it by clicking the toolbar button, `Erase Active Shape`.  The edit colors button will pop up as a floating icon, and clicking on that will display the color palette.

![Edit Colors](chart7.png)

### Export Tools

The two buttons at the far-right of the toolbar are for saving the raw data or, to save an image file of the chart at the current panned and zoomed view.

![Export Tools](chart8.png)

### Overlay

The button, `Overlay chart from CSV`, provides an easy import method for supplementing a chart with additional data.  Clicking on the button opens a pop-up dialogue to select the file, column, and whether the overlay should be a bar, candlestick, or line chart.  As a candlestick, the CSV file must contain OHLC data.  The import window can also be opened with the keyboard, `ctrl-o`.

![Overlay CSV](chart9.png)

After choosing the file to overlay, select what to show and then click on `Submit`.

![Overlay Options](chart10.png)

![Overlay Chart](chart11.png)

## Tables

The OpenBB Terminal sports interactive tables which opens in a separate window. They provide methods for searching, sorting, filtering, and exporting directly within the table.  Like the charts, both light and dark themes are included.  This preference can be set globally in the settings menu, or individually on the table with the click of a mouse.

### Setting the Theme

Set the theme, globally, as either light or dark.

Dark mode:

```console
/settings/table -s dark
```

Light mode:

```console
/settings/table -s light
```

The default state is dark mode.

![Dark Mode Tables](tables1.png)

### Sorting and Filtering

Columns can be sorted ascending/descending/unsorted, by clicking the controls to the right of each header title.  The status of the filtering is shown as a blue indicator.

![Sort Columns](tables2.png)

The settings button, at the lower-left corner, displays choices for customizing the table.  By selecting the `Type` to be `Advanced`, columns become filterable.

![Table Settings](tables3.png)

The columns can be filtered with min/max values or by letters, depending on the content of each column.

![Filtered Tables](tables4.png)

### Selecting Columns and Rows

The table will scroll to the right as far as there are columns.  Columns can be removed from the table by clicking the icon to the right of the settings button and unchecking it from the list.

![Select Columns](tables5.png)

The number of rows per page is defined in the drop down selection near the center, at the bottom.

![Rows per Page](tables6.png)

### Exporting Data

At the bottom-right corner of the table window, there is a button for exporting the data.  To the left, the drop down selection for `Type` can be defined as a CSV, XLSX, or PNG file.  Exporting the table as a PNG file will create a screenshot of the table at its current view, and data that is not on the screen will not be captured.

![Export Data](tables7.png)
