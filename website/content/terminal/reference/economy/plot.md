---
title: plot
description: OpenBB Terminal Function
---

# plot

This command can plot any data on two y-axes obtained from the macro, fred, index and treasury commands. To be able to use this data, just load the available series from the previous commands. For example 'macro -p GDP -c Germany Netherlands' will store the data for usage in this command. Therefore, it allows you to plot different time series in one graph. The example above could be plotted the following way: 'plot --y1 Germany_GDP --y2 Netherlands_GDP' or 'plot --y1 Germany_GDP Netherlands_GDP'

### Usage

```python
plot [--y1 YAXIS1] [--y2 YAXIS2]
```

---

## Parameters

| Name | Description | Default | Optional | Choices |
| ---- | ----------- | ------- | -------- | ------- |
| yaxis1 | Select the data you wish to plot on the first y-axis. You can select multiple variables here. |  | True | None |
| yaxis2 | Select the data you wish to plot on the second y-axis. You can select multiple variables here. |  | True | None |

![Figure_1](https://user-images.githubusercontent.com/46355364/158633367-783d54eb-79ab-443f-af99-8a9ecadf5949.png)

![Figure_2](https://user-images.githubusercontent.com/46355364/158633394-d948d909-d39b-4b05-9c5b-2e30b202cc32.png)

---
