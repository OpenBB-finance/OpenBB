```
usage: plot
            [-c {OPTIONS}]
            [-h] [--export {png,jpg,pdf,svg}]

```

Plot data based on the index. This functionality does not work for Panel Data unless 
creating a subset of the data that has only a singular index.

```
optional arguments:
  -c {OPTIONS} --column {OPTIONS}
                        Column to plot along the index (default: None)
  -h, --help            show this help message (default: False)
  --export {png,jpg,pdf,svg}
                        Export figure into png, jpg, pdf, svg (default: )

```

Example:
```
2022 Feb 25, 08:59 (✨) /statistics/ $ load TSLA_20220221_101033.xlsx tsla

2022 Feb 25, 09:04 (✨) /statistics/ $ plot adj_close-tsla
```

![adj_close_plot_tesla](https://user-images.githubusercontent.com/46355364/155728528-a1ae641b-fad3-4ae4-be3f-98abcdbf08e8.png)
