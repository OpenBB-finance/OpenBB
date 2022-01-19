```
usage: plot [-y {colnorm,col2,colnorm3,colb}] [-x {colnorm,col2,colnorm3,colb}] [-k {line,scatter,bar,barh,hist,box,kde,area,pie,hexbin}] [-h] [--export {png,jpg,pdf,svg}]
```
Plot 2 columns of loaded data.

```
optional arguments:
  -y {colnorm,col2,colnorm3,colb}
                        Variable to plot along y (default: None)
  -x {colnorm,col2,colnorm3,colb}, --vs {colnorm,col2,colnorm3,colb}
                        Variable along x axis (default: )
  -k {line,scatter,bar,barh,hist,box,kde,area,pie,hexbin}, --kind {line,scatter,bar,barh,hist,box,kde,area,pie,hexbin}
                        Type of plot for data (default: scatter)
  -h, --help            show this help message (default: False)
  --export {png,jpg,pdf,svg}
                        Export figure into png, jpg, pdf, svg (default: )
```

Note that when no "-x/--vs" is supplied, the x axis will be the dataframe index.  The -x and -y defaults will be the
columns present in your data.  In this scenario, the columns loaded are `colnorm,col2,colnorm3,colb` .

The different kinds of plots can be seen in the `kind` kwarg of the 
[pandas plot function](https://pandas.pydata.org/docs/reference/api/pandas.DataFrame.plot.html)