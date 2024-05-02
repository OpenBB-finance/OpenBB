---
title: The Pipeline of Commands
sidebar_position: 1
description: This page provides a detailed explanation of the OpenBB Platform CLI command pipeline.
  The tutorial video and walkthrough guides users in automating their investment
  research process by using single commands, and sequences of commands,
  to manipulate and study data.
keywords:
- Hub
- Routine
- Community Routines
- Terminal
- Architecture
- EXE
- Script
- Single command
- Pipeline of commands
- Command sequence
- Automate investment research
- Tutorial video
- GME's dark pool data
- Technical Analysis
- Moving Average Convergence/Divergence indicator
- Stock price loaded
- Exponential moving average indicator
- Price vs Short interest
---

import HeadTitle from '@site/src/components/General/HeadTitle.tsx';

<HeadTitle title="The Pipeline of Commands - Routines - Usage | OpenBB Platform CLI Docs" />

import TutorialVideo from '@site/src/components/General/TutorialVideo.tsx';

<TutorialVideo
    youtubeLink="https://www.youtube.com/embed/j0yZ9BMKulk?si=_CuDhd19pUs_mFDs"
    videoLegend="Short video on pipeline of commands"
/>

:::note
Note that the commands and menus may vary.
:::

## Single Command

If you have a good understanding of the Platform CLI's architecture, you will recognize that commands and menus are organized in the form of a tree.

![image](https://github.com/OpenBB-finance/OpenBBTerminal/assets/25267873/a5f10833-9693-4b39-9491-b431919db828)

If the intention is to explore an equity, enter at base of the menu (`/equity/`), then browse or navigate towards the point of interest - for example, Dark Pools (`/equity/darkpool`).

While all the information is in one place, having to type one command at a time is far from optimal.

## Pipeline of Commands

One of the main objectives of the OpenBB Platform CLI was the ability to automate a user's investment research workflow - not just a single command, but the complete process.  This is where the pipeline of commands comes in,  running a sequence of commands.

An example of a pipeline of commands is:

```console
/equity/price/historical --symbol AAPL/../../technical/ema --data 0 --length 50
```

Which will perform a exponential moving average (`ema`) on the historical price of Apple (`AAPL`).

### Step-by-Step Explanation

This will do the following:

1. `equity` - Go into `equity` menu

2. `price` - Go into `price` sub-menu

3. `historical --symbol AAPL` - Load historical price data for Apple

4. `technical` -  Go into Technical Analysis (`technical`) menu

5. `ema --data 0 --length 50` - Run the exponential moving average indicator with windows of length 50 (`--length 50`) on the last cached result (`--data 0`)
