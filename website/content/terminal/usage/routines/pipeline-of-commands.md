---
title: Pipeline of commands
sidebar_position: 1
description: Provides a brief overview of how to interact with the OpenBB Terminal
keywords: [finance, terminal, command line interface, cli, menu, commands]
---

import TutorialVideo from '@site/src/components/General/TutorialVideo.tsx';

<TutorialVideo
    youtubeLink="https://www.youtube.com/embed/j0yZ9BMKulk?si=_CuDhd19pUs_mFDs"
    videoLegend="Short video on pipeline of commands"
/>

One of the main objectives with the OpenBB Termina was the capability to be able to automate user's investment research workflow. Thus we needed to go further than just allowing to run 1 command at a time.

This is where the concept of pipeline of commands comes in. So users are able to run a sequence of commands, for instance:

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
