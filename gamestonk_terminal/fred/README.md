# fred

The purpose of fred is to have the ability to look at economic data.

* [GDP](#GDP)
    * Get GDP data
    
## GDP <a name="GDP"></a>
```text
usage: GDP [-n N_TO_GET] [-s START_DATE] [-p PLOT]]
```
Gets GDP data.  Data is released quarterly
* -n : Number of points to display.  If unspecified, it will display all available.
* -s : Start Date.  Format m/d/y. First point to get
* -p : Option to plot.  Defaults to False

To get the last 20 reported GDP values:
````
GDP -n 20
````
To plot all GDP data since 1/1/2010:
````
GDP -s 1/1/2010 -p True
````