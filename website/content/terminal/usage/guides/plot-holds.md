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

A chart is often only as good as its labelling.  On the previous example, we can see that the legends reflected the command paths that were used, but not the arguments.  If we added gdp of a second country, we would not be able to tell which line is which country.  In order to avoid this confusion, when the hold state is on, every function comes with a `--label` argument.  This will pass the users desired label into the chart legend.
