---
title: plot
description: OpenBB Terminal Function
---

# plot

This command can plot any data on two y-axes obtained from the macro, fred, index and treasury commands. To be able to use this data, just load the available series from the previous commands. For example 'macro -p GDP -c Germany Netherlands' will store the data for usage in this command. Therefore, it allows you to plot different time series in one graph. The example above could be plotted the following way: 'plot --y1 Germany_GDP --y2 Netherlands_GDP' or 'plot --y1 Germany_GDP Netherlands_GDP'

### Usage

```python
usage: plot [--y1 YAXIS1] [--y2 YAXIS2]
```

---

## Parameters

| Name | Description | Default | Optional | Choices |
| ---- | ----------- | ------- | -------- | ------- |
| yaxis1 | Select the data you wish to plot on the first y-axis. You can select multiple variables here. |  | True | None |
| yaxis2 | Select the data you wish to plot on the second y-axis. You can select multiple variables here. |  | True | None |
---

