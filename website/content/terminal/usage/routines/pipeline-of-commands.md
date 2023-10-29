---
title: Pipeline of commands
sidebar_position: 1
description: This page provides a detailed understanding of how to use OpenBB Terminal.
  The tutorial video and walkthrough guides to help users automate their investment
  research process by using single commands and command sequences to manipulate and
  study data, especially GME's dark pool data. Concepts like pipelines of commands,
  loading stocks, and use of indicators like MACD and EMA are explained.
keywords:
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

<HeadTitle title="Pipeline of commands - Routines - Usage | OpenBB Terminal Docs" />

import TutorialVideo from '@site/src/components/General/TutorialVideo.tsx';

<TutorialVideo
    youtubeLink="https://www.youtube.com/embed/j0yZ9BMKulk?si=_CuDhd19pUs_mFDs"
    videoLegend="Short video on pipeline of commands"
/>

## Single command

If you understand well the terminal architecture, you understand that commands and menus are organized in the form of a tree.

![image](https://github.com/OpenBB-finance/OpenBBTerminal/assets/25267873/a5f10833-9693-4b39-9491-b431919db828)

This means that if your intention is to explore GME's dark pool data, you simply need to navigate to the `stocks` section within the OpenBB Terminal and then proceed to the `dps` subsection (which stands for "dark pool and short" data). Upon reaching this point, the terminal will present you with several available commands that you could execute to retrieve the desired data.

While all the information is in one place, having to type one command at a type is far from optimal.

![image](https://github.com/OpenBB-finance/OpenBBTerminal/assets/25267873/41737800-7c60-48ad-a43d-814016d81762)

## Pipeline of commands

One of the main objectives of the OpenBB Terminal was the capability to be able to automate user's investment research workflow. Thus we needed to go further than just allowing to run 1 command at a time.

This is where the concept of a pipeline of commands comes in. So users can run a sequence of commands. For instance, the example above could be achieved by simply running

```console
(🦋) / $ stocks/load GME/dps/psi
```

Achieving the following:

![image](https://github.com/OpenBB-finance/OpenBBTerminal/assets/25267873/c21c5452-5a67-4384-851c-d2801b60f8cd)

A different example could be:

```console
(🦋) / $ stocks/load GME/dps/psi/../fa/pt/income/../ins/stats
```

![image](https://github.com/OpenBB-finance/OpenBBTerminal/assets/25267873/61db4010-bdc2-4851-9e47-79fb4425b816)

### Step-by-step explanation

```console
(🦋) / $ stocks/load amzn/ta/macd/ema -l 50,200/../dps/psi
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
