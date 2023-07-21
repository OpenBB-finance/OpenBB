---
sidebar_position: 7
title: Plot Hold
description: Learn how to use the `hold` functionality to overlay multiple datasets onto the same axes.
keywords: [openbb, openbb terminal, charting, matlab, hold, hodl, plotting, comparison]
---

import HeadTitle from '@site/src/components/General/HeadTitle.tsx';

<HeadTitle title="Plot Hold - Terminal | OpenBB Docs" />

As of OpenBB Terminal v3.2.0, the `hold` functionality is available to allow users to overlay multiple datasets onto the same axes. This is useful for comparing datasets, or for plotting multiple datasets that share the same x-axis.  This guide will walk through the functionalities and the recommended workflow.

Drawing inspiration from MatLab, the `hold` function is used to toggle the holding state of the current figure.  Unlike MatLab, this function needs to be called before calling any function that charts.  The hold state can be turned on by running

```bash
hold on
```
from any terminal menu.  By default, new plots will be placed on a new axis, meaning comparing the magnitude values can be tricky.  If you wish to plot subsequent figures on the same axis, you can use the sameaxis argument:

```bash
hold on --sameaxis
```

Once the hold state is turned on, any terminal command with a plot will not be shown until the hold is turned off.  To turn off the hold state, and see the combined figure, run:

```bash
hold off
```

An example workflow is as follows.  What this will do is plot the CPI and the GDP of the United States on the same axis.

```
2023 Jul 19, 14:52 [openbb_coo] 🦋 /economy/ $ hold on
2023 Jul 19, 14:52 [openbb_coo] 🦋 /economy/ $ gdp -c united_states
2023 Jul 19, 14:52 [openbb_coo] 🦋 /economy/ $ cpi -c united_states
2023 Jul 19, 14:52 [openbb_coo] 🦋 /economy/ $ hold off
```
Which results in the following figure:

![hold on ex1](https://github.com/OpenBB-finance/OpenBBTerminal/assets/18151143/a3b1f09e-1a64-4af0-a5a2-070590d848e1)

To show the impact of the `--sameaxis` argument, we can run the previous commands, but starting with `hold on --sameaxis`.  Because GDP is on the order on 70,000 USD/capita and the CPI is on the order of 10 (percent), we will see the cpi being a flat line, and the trend will not be apparent:

![hold on ex2](https://github.com/OpenBB-finance/OpenBBTerminal/assets/18151143/43219ca7-126b-4782-bd95-5fa8967e0c6c)


## Customizing Charts

A chart is often only as good as its labelling.  On the previous example, we can see that the legends reflected the command paths that were used, but not the arguments.  If we added gdp of a second country, we would not be able to tell which line is which country.  In order to avoid this confusion, when the hold state is on, every function comes with a `--legend` argument.  This will pass the users desired label into the chart legend.  When the chart is displayed, the legends will display.  If a command is run without the --legend argument, it will default to using the command location as previously shown.  In rare cases, a legend may not appear due to it not being defined in the functions `view` file.  In this case, please raise a GitHub issue so the team can address it.

An additional customization is the ability to add a custom title to the chart.  This can be specified by adding the `--title`` argument to the hold off functionality.  To show off these capabilities, we can use an example of plotting income statement items for different companies.  In this example, we can look at FAANG companies and plot their revenues on the same axis.  This example will show the previous 40 quarters.

```
2023 Jul 19, 15:31 [openbb_coo] 🦋 /stocks/fa/ $ hold on --sameaxis
2023 Jul 19, 15:31 [openbb_coo] 🦋 /stocks/fa/ $  income -t AAPL -q -l 40 --plot revenue --legend AAPL Revenue
2023 Jul 19, 15:31 [openbb_coo] 🦋 /stocks/fa/ $  income -t META -q -l 40 --plot revenue --legend META
2023 Jul 19, 15:31 [openbb_coo] 🦋 /stocks/fa/ $  income -t AMZN -q -l 40 --plot revenue
2023 Jul 19, 15:31 [openbb_coo] 🦋 /stocks/fa/ $  income -t GOOG -q -l 40 --plot revenue --legend GOOG
2023 Jul 19, 15:31 [openbb_coo] 🦋 /stocks/fa/ $  income -t NFLX -q -l 40 --plot revenue --legend netflix
2023 Jul 19, 15:31 [openbb_coo] 🦋 /stocks/fa/ $ hold off --title FAANG Revenues 10 Year
```

Which results in the following figure:

![hold on custom](https://github.com/OpenBB-finance/OpenBBTerminal/assets/18151143/793d8309-6e49-42ca-b9bd-ff0dad9da959)

<details>
<summary>Running with a routine</summary>
This functionality is able to be used in a [script routine](https://docs.openbb.co/terminal/usage/guides/scripts-and-routines)

The previous terminal example can be expressed as the following routine:
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
</details>

## Known Issues


Unfortunately, there are some known issues with the hold functionality.  These are being worked on, and will be addressed in future releases.  The following are known issues:

- When plotting charts,  if the x axes are not the same, there may be an undesired result.  For example, if looking at the `fixedincome/ycrv` function, the x axes is a number in years, so trying to plot a date along x will not work.
- Candle charts are not supported within the hold state.  A work around to plot a close value would be to navigate to `qa/pick Close/line`, which will plot a line chart.
- Figures that have subplots on their own are not supported.  This functionality is meant to overlay data on the same axes, so if there are multiple subplots, it is not supported.  An example would be a function like `ta/macd`.  The TA functions already have a multiple indicator functionality.
- Running a single plot in the hold state messes with the figure layout and does not give the desired margin.
- Time series data of varying frequencies may not produce smooth visuals.
