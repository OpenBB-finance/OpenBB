---
title: Basics
description: An introduction to the The OpenBB Terminal, a Command Line Interface (CLI) application.  Functions (commands) are called through the keyboard with results returning as charts, tables, or text.
keywords: [basics, commands, functions, features, menus, introduction, openbb terminal, obb, usage, how to, charts, tables, themes, styles, functions, data, sources, getting started]
---

## Overview

import HeadTitle from '@site/src/components/General/HeadTitle.tsx';

<HeadTitle title="Basics - Terminal | OpenBB Docs" />

The OpenBB Terminal is a Command Line Interface (CLI) application.  Functions (commands) are called through the keyboard with results returned as charts, tables, or text.  Charts and tables (if enabled) are displayed in a new window, and are fully interactive, while text prints directly to the Terminal screen.  Commands are grouped into menus, with a menu or sub-menu being visually distinguishable from a function by the, `>`, on the far left of the screen.  The color of the text can be altered under the [`/settings` menu](https://docs.openbb.co/terminal/usage/guides/customizing-the-terminal).

Navigating through the Terminal menus is similar to following down a path, or traversing folders from any operating system's command line prompt.  The `/home` screen is the main path where everything begins, and the menus are paths branched from the main.  Instead of `C:\Users\OpenBB\Documents`, it is, [`/stocks/options`](https://docs.openbb.co/terminal/usage/intros/stocks/options). Instead of, `cd ..`, two periods - `..` - returns to the menu one level back towards the home screen.

:::note
Absolute paths are also valid to-and-from any point.  From the [`/stocks/options`](https://docs.openbb.co/terminal/usage/intros/stocks/options) menu, go directly to [`/crypto`](https://docs.openbb.co/terminal/usage/intros/crypto).  By itself, `/`, returns to the home level.
:::

![The Home Screen](https://user-images.githubusercontent.com/85772166/233247655-2f8d0dae-be68-48ca-9b35-123b5b985cb6.png)

## Auto Complete

The OpenBB Terminal is equipped with an auto completion engine that presents choices based on the current menu.  Whenever you start typing, the prompt will appear. When the function contains arguments, pressing the `space bar` after typing the command will present the list of available arguments.  This functionality dramatically reduces the number of key strokes required to perform tasks and, in many cases, eliminates the need to consult the help dialogue for reminders.  Choices - where they are bound by a defined list - are searchable with the up and down arrow keys.

![Auto Complete](https://user-images.githubusercontent.com/85772166/233247702-f707531c-2c65-4380-a662-cd4bc2ae0199.png)

## Help Dialogues

### -h or --help

A help dialogue for any function at the current location is printed to the screen by typing `-h` after the command.  The information returned contains a short description of the function and all accepted arguments.  For an example, the `/news` function:

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

To search for news containing the term, "Federal Reserve", try this command:

```console
/news --term Federal Reserve
```

### About

`about` is a global function that opens a browser to the OpenBB documentation pages at the specific command or menu.

```console
/about stocks
```

The command above will open a browser to [Introduction to the Stocks menu](https://docs.openbb.co/terminal/usage/intros/stocks).

### Support

`support` is a global function for submitting a new request for support, a general question, or a bug report.  The command will pre-populate a form with key information, like the command or menu name specific to the issue.  Use the up and down arrow keys to browse and select the appropriate item for the ticket.  Naturally, this command has a help dialogue.

```console
support -h
```

```console
Submit your support request

options:
  -c {search,load,quote,tob,candle,news,resources,codes,ta,ba,qa,disc,dps,scr,sia,ins,gov,res,dd,fa,bt,ca,options,th,forecast}, --command {generic,search,load,quote,tob,candle,news,resources,codes,ta,ba,qa,disc,dps,scr,sia,ins,gov,res,dd,fa,bt,ca,options,th,forecast}
                        Command that needs support (default: None)
  --msg MSG [MSG ...], -m MSG [MSG ...]
                        Message to send. Enclose it with double quotes (default: )
  --type {bug,suggestion,question,generic}, -t {bug,suggestion,question,generic}
                        Support ticket type (default: generic)
  -h, --help            show this help message (default: False)
```

![Support](https://user-images.githubusercontent.com/85772166/233577183-fbeb7be2-1d00-4ca0-86b3-42f1b71081e8.png)

```console
support search --type question --msg "How do I find stocks from India with OpenBB?"
```

![Support Auto Complete](https://user-images.githubusercontent.com/85772166/233577389-f0ad1b08-0e22-44b1-9d6b-9732c77af7d7.png)

The command opens a browser window to a pre-populated form on the OpenBB website.  If you are signed-in to the Hub, all that is left to do is click `Submit`.

![Submit Form](https://user-images.githubusercontent.com/85772166/233577448-3e426a88-d0cf-4338-8f4c-21b9fd01d8b2.png)

**An answer to this question is**: `search --country india --exchange-country india`

:::note
Tips for submitting a support request:

- Tell us what version number is installed.
- Tell us what operating system and version the machine has.
- What is the installation type?  Installer, Source, PyPi, Docker, other?
- Tell us the command and parameter combination causing the error.
- Tell us what symbol (ticker) is, or was trying to be, loaded.
- Show us the complete error message.
- Let us know any contextual information that will help us replicate and accurately identify the problem.
:::

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

The commands listed below are not displayed on any Terminal menu, but are available from any location in the Terminal.

| Function Key |                                       Description |
| :----------- | ------------------------------------------------: |
| cls          |                       Clears the Terminal screen. |
| exit         |                               Quits the Terminal. |
| help, h, ?   |                   Prints the current menu screen. |
| quit, q, ..  |             Navigates back one menu towards Home. |
| reset, r     | Resets the Terminal, opening to the current menu. |

## Data

Many functions will require obtaining (free or subscription) API keys from various data providers.  OpenBB provides methods for consuming these data feeds, but has no control over the quality or quantity of data provided to an end-user.   **No API Keys are required to get started using the Terminal**.  See the list of data providers [here](https://docs.openbb.co/terminal/usage/guides/api-keys), along with instructions for entering the credentials into the OpenBB Terminal.  [Request a feature](https://openbb.co/request-a-feature) to let us know what we are missing!

### Default Data Sources

The default data source for each function (where multiple sources are available) can be defined within the [`/sources` menu](https://docs.openbb.co/terminal/usage/guides/changing-sources).  The available sources for each function are displayed on the right of the menu, and they can be distinguished by the square brackets and distinct font color group.  Unless a preference for a particular function is defined, the command will prioritize in the order they are displayed, from left-to-right, on the Terminal screen.  To override a preference or default source, select one of the other choices by attaching the, `--source`, argument to the command syntax.  The available sources for the feature will be populated by auto complete when the `space bar` is pressed after typing `--source`.  This information is also printed with the `--help` dialogue of a command.

```console
/stocks/load AAPL/fa/income --source Polygon
```

![Selecting a new Data Source](https://user-images.githubusercontent.com/85772166/233730763-54fd6400-f3ad-44a0-9c73-254d91ac2085.png)

### Importing and Exporting Data

Most functions provide a method for exporting the raw data as a CSV, JSON, or XLSX file (with a specific sheet name).  Exported data and user-supplied files to import are saved to the [OpenBBUserData folder](https://docs.openbb.co/terminal/usage/guides/data).  The folder is located at the root of the operating system's User Account folder.  Follow the link for a detailed description.

## Charts

The OpenBB charting library provides interactive, customizable, charts.  Here's an example of displaying weekly candles for AAPL.

```console
/stocks/load AAPL -w/candle
```

![Apple Weekly Chart](https://user-images.githubusercontent.com/85772166/233247951-e011fe2c-23a6-4518-bd17-3f43a9c2011a.png)

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

![Chart Tools](https://user-images.githubusercontent.com/85772166/233247997-55c03cbd-9ca9-4f5e-b3fb-3e5a9c63b6eb.png)

Toggle the toolbar's visibility via the keyboard with, `ctrl + h`.

### Text Tools

Annotate a chart by clicking on the `Add Text` button, or with the keyboard, `ctrl + t`.

![Annotate Charts](https://user-images.githubusercontent.com/85772166/233248056-d459d7a0-ba2d-4533-896a-79406ded859e.png)

Enter some text, make any adjustments to the options, then `submit`.  Place the crosshairs over the desired data point and click to place the text.

![Place Text](https://user-images.githubusercontent.com/85772166/233728645-74734241-4da2-4cff-af17-b68a62e95113.png)

After placement, the text can be updated or deleted by clicking on it again.

![Delete Annotation](https://user-images.githubusercontent.com/85772166/233728428-55d2a8e5-a68a-4cd1-9dbf-4c1cd697187e.png)

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

![Edit Colors](https://user-images.githubusercontent.com/85772166/233729318-8af947fa-ce2a-43e2-85ab-657e583ac8b1.png)

### Export Tools

The two buttons at the far-right of the toolbar are for saving the raw data or, to save an image file of the chart at the current panned and zoomed view.

![Export Tools](https://user-images.githubusercontent.com/85772166/233248436-08a2a463-403b-4b1b-b7d8-80cd5af7bee3.png)

### Overlay

The button, `Overlay chart from CSV`, provides an easy import method for supplementing a chart with additional data.  Clicking on the button opens a pop-up dialogue to select the file, column, and whether the overlay should be a bar, candlestick, or line chart.  As a candlestick, the CSV file must contain OHLC data.  The import window can also be opened with the keyboard, `ctrl-o`.

![Overlay CSV](https://user-images.githubusercontent.com/85772166/233248522-16b539f4-b0ae-4c30-8c72-dfa59d0c0cfb.png)

After choosing the file to overlay, select what to show and then click on `Submit`.

![Overlay Options](https://user-images.githubusercontent.com/85772166/233250634-44864da0-0936-4d3c-8de2-c8374d26c1d2.png)

![Overlay Chart](https://user-images.githubusercontent.com/85772166/233248639-6d12b16d-471f-4550-a8ab-8d8c18eeabb3.png)

### Cheat Sheet

The image below can be saved and used as a reference.

![Group 653](https://user-images.githubusercontent.com/85772166/234313541-3d725e1c-ce48-4413-9267-b03571e0eccd.png)


## Tables

The OpenBB Terminal sports interactive tables which opens in a separate window. They provide methods for searching, sorting, filtering, and exporting directly within the table.  Preferences and settings for the tables can be updated directly on the table.

### Sorting and Filtering

Columns can be sorted ascending/descending/unsorted, by clicking the controls to the right of each header title.  The status of the filtering is shown as a blue indicator.

![Sort Columns](https://user-images.githubusercontent.com/85772166/233248754-20c18390-a7af-490c-9571-876447b1b0ae.png)

The settings button, at the lower-left corner, displays choices for customizing the table.  By selecting the `Type` to be `Advanced`, columns become filterable.

![Table Settings](https://user-images.githubusercontent.com/85772166/233248876-0d788ff4-974d-4d92-8186-56864469870a.png)

The columns can be filtered with min/max values or by letters, depending on the content of each column.

![Filtered Tables](https://user-images.githubusercontent.com/85772166/233248923-45873bf1-de6b-40f8-a4aa-05e7c3d21ab0.png)

### Selecting Columns and Rows

The table will scroll to the right as far as there are columns.  Columns can be removed from the table by clicking the icon to the right of the settings button and unchecking it from the list.

![Select Columns](https://user-images.githubusercontent.com/85772166/233248976-849791a6-c126-437c-bb54-454ba6ea4fa2.png)

The number of rows per page is defined in the drop down selection near the center, at the bottom.

![Rows per Page](https://user-images.githubusercontent.com/85772166/233249018-8269896d-72f7-4e72-a4d4-2715d1f11b96.png)

### Freeze the Index and Column Headers

Right-click on the index name to enable/disable freezing when scrolling to the right.  Column headers are frozen by default.

![Index Freeze](https://user-images.githubusercontent.com/85772166/234103702-0965dfbd-24ca-4a66-8c76-9fac28abcff8.png)

### Exporting Data

At the bottom-right corner of the table window, there is a button for exporting the data.  To the left, the drop down selection for `Type` can be defined as a CSV, XLSX, or PNG file.  Exporting the table as a PNG file will create a screenshot of the table at its current view, and data that is not on the screen will not be captured.

![Export Data](https://user-images.githubusercontent.com/85772166/233249065-60728dd1-612e-4684-b196-892f3604c0f4.png)

### Cheat Sheet

The image below can be saved and used as a reference.

![Chart Intro (5)](https://user-images.githubusercontent.com/85772166/234315026-de098953-111b-4b69-9124-31530c01407a.png)
