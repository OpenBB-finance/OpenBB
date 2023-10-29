---
title: Overlay financial data
sidebar_position: 2
description: Guide to improve financial data comparison and visualization using the
  'hold on' command in OpenBBTerminal. Covers overlaying data on the same axes, customizing
  chart legends and titles, analyzing FAANG companies and GDP/CPI data, and more.
keywords:
- hold on command
- overlay financial data
- same axis plotting
- customizing charts
- financial data comparison
- MatLab
- financial charts
- FAANG companies
- CPI
- GDP
- data visualization
---

import HeadTitle from '@site/src/components/General/HeadTitle.tsx';

<HeadTitle title="Overlay financial data - Routines - Usage | OpenBB Terminal Docs" />

import TutorialVideo from '@site/src/components/General/TutorialVideo.tsx';

<TutorialVideo
    youtubeLink="https://www.youtube.com/embed/GZ20uk4o2Nk?si=vxeA-CxSUq85R_zj"
    videoLegend="Short video on how to use hold on command to overlay financial data"
/>

## Hold on command

Often analysts want to be able to overlay financial data. This is possible through the introduction of the `hold on` command.

The `hold` functionality is available to allow users to overlay multiple datasets onto the same chart axes. This is useful for comparing datasets, or for plotting multiple datasets that share the same x-axis. This guide will walk through the functionalities and the recommended workflow.

Drawing inspiration from MatLab, the `hold` function is used to toggle the holding state of the current figure. Unlike MatLab, this function needs to be called before calling any function that charts. The hold state can be turned on, from any terminal menu, by running:

```bash
hold on
```

By default, new plots will be placed on a new axis, meaning comparing the magnitude values can be tricky. If you wish to plot subsequent figures on the same axis, you can use the sameaxis argument:

```bash
hold on --sameaxis
```

Once the hold state is turned on, any terminal command with a plot will not be shown until the hold is turned off. To turn off the hold state, and see the combined figure, run:

```bash
hold off
```

An example workflow is as follows. What this will do is plot the CPI and the GDP of the United States on the same axis.

```
(🦋) /economy/ $ hold on
(🦋) /economy/ $ gdp -c united_states
(🦋) /economy/ $ cpi -c united_states
(🦋) /economy/ $ hold off
```
Which results in the following figure:

![hold on ex1](https://github.com/OpenBB-finance/OpenBBTerminal/assets/18151143/a3b1f09e-1a64-4af0-a5a2-070590d848e1)

To show the impact of the `--sameaxis` argument, we can run the previous commands, but starting with `hold on --sameaxis`. Because GDP is on the order on 70,000 USD/capita and the CPI is on the order of 10 (percent), we will see the cpi being a flat line, and the trend will not be apparent:

![hold on ex2](https://github.com/OpenBB-finance/OpenBBTerminal/assets/18151143/43219ca7-126b-4782-bd95-5fa8967e0c6c)


## Customizing Charts

A chart is only as good as its labelling. On the previous example, we can see that the legends reflected the command paths that were used, but not the arguments. If we added gdp of a second country, we would not be able to tell which line is which country. In order to avoid this confusion, when the hold state is on, every function comes with a `--legend` argument.

This will pass the users desired label into the chart legend. When the chart is displayed, the legends will display. If a command is run without the `--legend` argument, it will default to using the command location as previously shown. In rare cases, a legend may not appear due to it not being defined in the functions `view` file. In this case, please raise a [GitHub issue](https://github.com/OpenBB-finance/OpenBBTerminal/issues/new/choose) so the team can address it.

An additional customization is the ability to add a custom title to the chart. This can be specified by adding the `--title` argument to the hold off functionality. To show off these capabilities, we can use an example of plotting income statement items for different companies. In this example, we can look at FAANG companies and plot their revenues on the same axis. This example will show the previous 40 quarters.

```
(🦋) /stocks/fa/ $ hold on --sameaxis
(🦋) /stocks/fa/ $  income -t AAPL -q -l 40 --plot revenue --legend AAPL Revenue
(🦋) /stocks/fa/ $  income -t META -q -l 40 --plot revenue --legend META
(🦋) /stocks/fa/ $  income -t AMZN -q -l 40 --plot revenue
(🦋) /stocks/fa/ $  income -t GOOG -q -l 40 --plot revenue --legend GOOG
(🦋) /stocks/fa/ $  income -t NFLX -q -l 40 --plot revenue --legend netflix
(🦋) /stocks/fa/ $ hold off --title FAANG Revenues 10 Year
```

Which results in the following figure:

![hold on custom](https://github.com/OpenBB-finance/OpenBBTerminal/assets/18151143/793d8309-6e49-42ca-b9bd-ff0dad9da959)

### Example as pipeline of commands

The following pipeline of commands can be run to achieve the same as above.

```console
(🦋) $ stocks/fa/hold on --sameaxis/income -t AAPL -q -l 40 --plot revenue --legend AAPL Revenue/income -t META -q -l 40 --plot revenue --legend META/income -t AMZN -q -l 40 --plot revenue/income -t GOOG -q -l 40 --plot revenue --legend GOOG/income -t NFLX -q -l 40 --plot revenue --legend netflix/hold off --title FAANG Revenues 10 Year
```

### Example as routine

Or, a user can create a routine that can be run by utilizing `exe` command.

```bash
    $STOCKS=AAPL,AMZN,MSFT,TSLA,GOOG

    stocks
    fa
    hold on --sameaxis

    foreach $$tick in $STOCKS:
        income -t $$tick -l 40 -q --plot revenue --legend $$tick revenue
    end

    hold off--title FAANG Revenues 10 Year
```

### Known Issues

Unfortunately, there are some known issues with the hold functionality. These are being worked on, and will be addressed in future releases. The following are known issues:

- When plotting charts, if the x axes are not the same, there may be an undesired result. For example, if looking at the `fixedincome/ycrv` function, the x axes is a number in years, so trying to plot a date along x will not work.

- Candle charts are not supported within the hold state. A work around to plot a close value would be to navigate to `qa/pick Close/line`, which will plot a line chart.

- Figures that have subplots on their own are not supported. This functionality is meant to overlay data on the same axes, so if there are multiple subplots, it is not supported. An example would be a function like `ta/macd`. The TA functions already have a multiple indicator functionality, `ta/multi`.

- Running a single plot in the hold state messes with the figure layout and does not give the desired margin.

- Time series data of varying frequencies may not produce smooth visuals.
