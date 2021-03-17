# FRED

The purpose of fred is to have the ability to look at economic data.

* [gdp](#gdp)
    * Get GDP data
* [cust](#cust)
    * Get custom fred data  

## gdp <a name="gdp"></a>
```text
usage: gdp [-n N_TO_GET] [-s START_DATE] [--noplot] [--hidedata]
```
Gets GDP data.  Data is released quarterly
* -n : Number of points to display.  If unspecified, it will display all available.
* -s : Start Date.  Format YYYY-mm-dd. First point to get.  Defaults to Jan 1 2015
* --noplot : Flag to hide plot
* --hidedata : Flag to suppress printing output

To get and plot the last 20 reported GDP values:
````
gdp -n 20 
````
To show all GDP data since 1/1/2016, with no plot.
````
gdp -s 2016-01-01 --noplot
````
Outputs:
````
                  GDP
Date                 
2016-01-01  18470.156
2016-04-01  18656.207
2016-07-01  18821.359
2016-10-01  19032.580
2017-01-01  19237.435
2017-04-01  19379.232
2017-07-01  19617.288
2017-10-01  19937.963
2018-01-01  20242.215
2018-04-01  20552.653
2018-07-01  20742.723
2018-10-01  20909.853
2019-01-01  21115.309
2019-04-01  21329.877
2019-07-01  21540.325
2019-10-01  21747.394
2020-01-01  21561.139
2020-04-01  19520.114
2020-07-01  21170.252
2020-10-01  21487.896
````


## cust <a name="cust"></a>

The fred database has many different datasets freely available.  They each have their own custom SERIES_ID which can be obtained through the website.

````
usage: cust [-i --id] [-s START_DATE] [--noplot] [--hidedata]
````
* -i/--id : Series ID for FRED data.  Required argument
* -s : Start Date.  Format YYYY-mm-dd. First point to get.  Defaults to Jan 1 2015.
* --noplot : Flag to suppress output plot.
* --hidedata : Flag to suppress data output

An example of custom data could be the unemployment rate.  According to https://fred.stlouisfed.org/series/UNRATE , the series ID is UNRATE.  So to plot this for 2019 to now

````
cust --id UNRATE -s 2019-01-01 
````
This will plot and display:


````
            UNRATE
Date              
2019-01-01     4.0
2019-02-01     3.8
2019-03-01     3.8
2019-04-01     3.7
2019-05-01     3.7
2019-06-01     3.6
2019-07-01     3.6
2019-08-01     3.7
2019-09-01     3.5
2019-10-01     3.6
2019-11-01     3.6
2019-12-01     3.6
2020-01-01     3.5
2020-02-01     3.5
2020-03-01     4.4
2020-04-01    14.8
2020-05-01    13.3
2020-06-01    11.1
2020-07-01    10.2
2020-08-01     8.4
2020-09-01     7.8
2020-10-01     6.9
2020-11-01     6.7
2020-12-01     6.7
2021-01-01     6.3
2021-02-01     6.2
````