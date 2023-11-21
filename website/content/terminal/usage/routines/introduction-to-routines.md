---
title: Introduction to Routines
sidebar_position: 2
description: The page provides a detailed introduction to OpenBB Routines, which allow
  users to automate processes and repetitive tasks in financial analysis and data
  collection. It explains basic scripts, routine execution, and guides users on getting
  started with an example.
keywords:
- OpenBB Routines
- automated processes
- repetitive tasks
- data collection
- basic script
- routine execution
- tutorial video
---

import HeadTitle from '@site/src/components/General/HeadTitle.tsx';

<HeadTitle title="Introduction to Routines - Routines - Usage | OpenBB Terminal Docs" />

import TutorialVideo from '@site/src/components/General/TutorialVideo.tsx';

<TutorialVideo
    youtubeLink="https://www.youtube.com/embed/p1pY6Zujvnc?si=HWStqbVnkU_Lw_P-"
    videoLegend="Show short introduction to OpenBB routines"
/>

## Introduction

OpenBB Routines allows users to capture and write simple scripts for automating processes and repetitive tasks. In essence, these are text plain-text files that can be created or modified in any basic text editor with the only difference being the `.openbb` extension.

Other software like STATA, SPSS, and R-Studio share similar functionality in the area of Econometrics and the OpenBB routine scripts venture into the area of financial analysis and data collection to speed up the process.

Routines make it easy to automate a series of processes, and this includes mining and dumping large amounts of data to organized spreadsheets.  Making use of `--export` and `--sheet-name`, data collection is more efficient and reliable, with results that are easily replicable.

A pipeline of commands is difficult to share, so to encourage users to share ideas and processes, we created [Community Routines](community-routines.md) for the [OpenBB Hub](https://my.openbb.co/).  Routines can be created, stored, and shared - executable in any Terminal installation, by URL.

## Routine execution

Run a routine file from the main menu, with the `exe` command. A great start would be to use `exe --example` to get a sense of what this functionality does. Below, the `--help` dialogue is displayed.

```console
/exe -h
```

```console
usage: exe [--file FILE [FILE ...]] [-i ROUTINE_ARGS] [-e] [--url URL] [-h]

Execute automated routine script. For an example, please use `exe --example` and for documentation and to learn how create your own script type `about exe`.

optional arguments:
  --file FILE [FILE ...], -f FILE [FILE ...]
                        The path or .openbb file to run. (default: None)
  -i ROUTINE_ARGS, --input ROUTINE_ARGS
                        Select multiple inputs to be replaced in the routine and separated by commas. E.g. GME,AMC,BTC-USD (default: None)
  -e, --example         Run an example script to understand how routines can be used. (default: False)
  --url URL             URL to run openbb script from. (default: None)
  -h, --help            show this help message (default: False)

For more information and examples, use 'about exe' to access the related guide.
```

## Basic Script

![image](https://github.com/OpenBB-finance/OpenBBTerminal/assets/25267873/eaeb3511-d544-4579-8d76-f7a4fd7bb1d3)

The most basic script style contains 2 main elements:

- **Comments**: any text after a hashtag (`#`) is referred to as a comment. This is used to explain what is happening within the line below and is ignored when the file is executed.
- **Commands**: any text *without* a hashtag is being run inside the OpenBB Terminal as if the user had prompted that line in the terminal. Note that this means that you are able to create a pipeline of commands in a single line, i.e. `stocks/load AAPL/candle --ma 20` is a valid line for the script.

For instance, the text below corresponds to the example file that OpenBB provides.

```console
# Go into the stocks context
stocks

# Load a company ticker, e.g. Apple
load AAPL

# Show a candle chart with a 20 day Moving Average
candle --ma 20

# Switch over to the Fundamental Analysis menu
fa

# Show Earnings per Share (EPS) estimates
epsfc

# Show price targets charts
pt

# Show future estimations
est

# Return to home
home
```

## Getting started

As a starting point, let's use the example above.

1. Create a new text file with the name `routines_template.openbb` and copy and paste the routine above.

2. Move the file inside the `routines` folder within the [OpenBBUserData](/terminal/usage/data/custom-data) folder and, optionally, adjust the name to your liking.

3. Open up the OpenBB Terminal, and type `exe --file routines_template`.  If you changed the name of the file, then replace, `routines_template`, with that.  As long as the file remains in the `~/OpenBBUserData/routines` folder, OpenBB Terminal's auto-completer will provide it as a choice.

When this routine is run, a candle chart with a moving average of 20 days, expectations and price targets from analysts and estimated future performance should pop up before returning to the home window.

![OpenBB Routine Script Execution](https://user-images.githubusercontent.com/46355364/223207167-dfab3a74-d34d-47d4-bf6e-44944e8fbfa2.png)
