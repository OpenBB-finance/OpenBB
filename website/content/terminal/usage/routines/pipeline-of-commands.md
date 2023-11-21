---
title: The Pipeline of Commands
sidebar_position: 1
description: This page provides a detailed explanation of the OpenBB Terminal command pipeline.
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

<HeadTitle title="The Pipeline of Commands - Routines - Usage | OpenBB Terminal Docs" />

import TutorialVideo from '@site/src/components/General/TutorialVideo.tsx';

<TutorialVideo
    youtubeLink="https://www.youtube.com/embed/j0yZ9BMKulk?si=_CuDhd19pUs_mFDs"
    videoLegend="Short video on pipeline of commands"
/>

## Single Command

If you have a good understanding of the Terminal's architecture, you will recognize that commands and menus are organized in the form of a tree.

![image](https://github.com/OpenBB-finance/OpenBBTerminal/assets/25267873/a5f10833-9693-4b39-9491-b431919db828)

If the intention is to explore an equity, enter at base of the menu (`/stocks/`), then browse or navigate towards the point of interest - for example, Dark Pools (`/stocks/dps`).

While all the information is in one place, having to type one command at a time is far from optimal.

![image](https://github.com/OpenBB-finance/OpenBBTerminal/assets/25267873/41737800-7c60-48ad-a43d-814016d81762)

## Pipeline of Commands

One of the main objectives of the OpenBB Terminal was the ability to automate a user's investment research workflow - not just a single command, but the complete process.  This is where the pipeline of commands comes in,  running a sequence of commands.

The example above can be recreated by running:

```console
/stocks/load GME/dps/psi
```

Which looks like:

![image](https://github.com/OpenBB-finance/OpenBBTerminal/assets/25267873/c21c5452-5a67-4384-851c-d2801b60f8cd)

Another example is:

```console
/stocks/load GME/dps/psi/../fa/pt/income/../ins/stats
```

![image](https://github.com/OpenBB-finance/OpenBBTerminal/assets/25267873/61db4010-bdc2-4851-9e47-79fb4425b816)

### Step-by-Step Explanation

```console
/stocks/load amzn/ta/macd/ema -l 50,200/../dps/psi
```

This will do the following:

1. `stocks` - Go into `stocks` menu

2. `load amzn` - Load Amazon's stock inside stock menu

3. `ta` - Go into Technical Analysis (`ta`) menu

4. `macd` - Run the moving average convergence/divergence indicator (`macd`) on the stock price loaded (i.e. `amzn`)

5. `ema -l 50,200` - Run the exponential moving average indicator with windows of length 50 and 200 (`ema -l 50,200`) on the stock price loaded (i.e. `amzn`)

6. `..` - Go one menu up

7. `dps` - Go into Dark pool and Short (`dps`) menu

8. `psi` - Go into Price vs Short interest (`psi`) menu
