---
title: Commands and arguments
sidebar_position: 2
description: This documentation page includes a tutorial video that provides a short
  introduction on commands and arguments for the OpenBB Platform CLI. It further explains
  the help dialogue for functions, the auto-completion feature, and global commands
  such as help, about, support, cls, quit, exit, and reset. Also, tips for submitting
  support requests are provided.
keywords:
- tutorial video
- help arguments
- auto-complete
- global commands
- support command
- reset command
- command line interface
- metadata
---

import HeadTitle from '@site/src/components/General/HeadTitle.tsx';

<HeadTitle title="Commands and arguments - Overview - Usage | OpenBB Platform CLI Docs" />

import TutorialVideo from '@site/src/components/General/TutorialVideo.tsx';

<TutorialVideo
    youtubeLink="https://www.youtube.com/embed/y8J7fGW9ZpY?si=ioMxKMCgD2X-MQ2j"
    videoLegend="Short introduction on commands and arguments"
/>

:::note
Note that the commands and menus may vary.
:::

## Help arguments

A help dialogue for any function at the current location is printed to the screen by typing `-h` or `--help` after the command. The information returned contains a short description of the function and all accepted arguments. For example the `news` command will return:

```console
(🦋) /news/ $ company --help

usage: company [--symbol SYMBOL [SYMBOL ...]] [--start_date START_DATE] [--end_date END_DATE] [--limit LIMIT] [--provider {benzinga,fmp,intrinio,polygon,tiingo,tmx,yfinance}]
               [--date DATE] [--display {headline,abstract,full}] [--updated_since UPDATED_SINCE] [--published_since PUBLISHED_SINCE] [--sort {id,created,updated}]
               [--order {asc,desc}] [--isin ISIN] [--cusip CUSIP] [--channels CHANNELS] [--topics TOPICS] [--authors AUTHORS] [--content_types CONTENT_TYPES] [--page PAGE]
               [--source {yahoo,moody,moody_us_news,moody_us_press_releases}] [--sentiment {positive,neutral,negative}] [--language LANGUAGE] [--topic TOPIC]
               [--word_count_greater_than WORD_COUNT_GREATER_THAN] [--word_count_less_than WORD_COUNT_LESS_THAN] [--is_spam]
               [--business_relevance_greater_than BUSINESS_RELEVANCE_GREATER_THAN] [--business_relevance_less_than BUSINESS_RELEVANCE_LESS_THAN] [--offset OFFSET] [-h]
               [--export EXPORT] [--sheet-name SHEET_NAME [SHEET_NAME ...]]

Company News. Get news for one or more companies.

optional arguments:
  --symbol SYMBOL [SYMBOL ...]
                        Symbol to get data for. Multiple comma separated items allowed for provider(s): benzinga, fmp, intrinio, polygon, tiingo, tmx, yfinance.
  --start_date START_DATE
                        Start date of the data, in YYYY-MM-DD format.
  --end_date END_DATE   End date of the data, in YYYY-MM-DD format.
  --limit LIMIT         The number of data entries to return.
  --provider {benzinga,fmp,intrinio,polygon,tiingo,tmx,yfinance}
                        The provider to use for the query, by default None.
                            If None, the provider specified in defaults is selected or 'benzinga' if there is
                            no default.
  -h, --help            show this help message
  --export EXPORT       Export raw data into csv, json, xlsx and figure into png, jpg, pdf, svg
  --sheet-name SHEET_NAME [SHEET_NAME ...]
                        Name of excel sheet to save data to. Only valid for .xlsx files.

```

To search for news for a certain ticker, you can use this command:

```console
(🦋) /news/ $ company --symbol aapl
```


## Auto-complete

![Auto Complete](https://user-images.githubusercontent.com/85772166/233247702-f707531c-2c65-4380-a662-cd4bc2ae0199.png)

The OpenBB Platform CLI is equipped with an auto completion engine that presents choices based on the current menu and command. Whenever you start typing, suggestion prompts will appear for existing commands and menus. When the command contains arguments, pressing the `space bar` after typing the command will present the list of available arguments. Note that a menu doesn't has arguments attached.

This functionality dramatically reduces the number of key strokes required to perform tasks and, in many cases, eliminates the need to consult the help dialogue for reminders. Choices - where they are bound by a defined list - are searchable with the up and down arrow keys.

## Global commands

These are commands that can be used throughout the CLI and will work regardless of the menu where they belong.

### Help

The `help` command shows the current menu you are in and all the commands and menus that exist, including a short description for each of these.

This is arguably one of the most helpful commands that the CLI. If you are familiar to navigating in a command line interface, it's the equivalent to `ls -ll`.

### CLS

The `cls` command clears the entire CLI screen.

### Quit

The `quit` command (can also use `q` or `..`) allows to leave the current menu to go one menu above. If the user is on the root, that will mean leaving the CLI.

### Exit

The `exit` command allows the user to exit the CLI.

### Reset

The `reset` command (or `r`) allows a developer that is using the CLI through source code to quickly test it's code changes by re-starting the CLI with the code changes. This allows to improve speed of development.
