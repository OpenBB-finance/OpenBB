# FRED

https://fred.stlouisfed.org

The purpose of fred is to have the ability to look at economic data.  This page offers 2 options:

* [predefined](#gdp)
    * Get predefined data
* [cust](#cust)
    * Get custom fred data  

The current predefined options are
* GDP
* 1,5,10,30 Year Treasury Rates
* 30 Year Mortgage Rates
* Unemployment Rate
* 3 Month LIBOR
* Moody's AAA Corporate Bond

## predefined <a name="predefined"></a>
```text
usage: selected [-n N_TO_GET] [-s START_DATE] [--noplot] [--hidedata]
```
Gets predefined data.  Arguments
* selected : Key from the predefined list.
* -s : Start Date.  Format YYYY-mm-dd. First point to get.  Defaults to Jan 1 2019
* --noplot : Flag to hide plot
* --hidedata : Flag to suppress printing output.  Useful for data released daily/weekly.

To plot the 30-Year Mortgage rates since 2018-01-01 suppressing the output.
````
mort30 -s 2018-01-01 --hidedata
````
To show all GDP data since 1/1/2016, with no plot.
````
gdp -s 2016-01-01 --noplot
````
Output:
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

An example of custom data could be the USD/EURO exchange rate.  
According to https://fred.stlouisfed.org/series/DEXUSEU , the series ID is DEXUSEU.  So to plot this from the start of February 2021 to now (3/17)

````
cust --id UNRATE -s 2021-02-01 
````
This will plot and display:

````
            DEXUSEU
Date               
2021-02-01   1.2070
2021-02-02   1.2020
2021-02-03   1.2025
2021-02-04   1.1974
2021-02-05   1.2035
2021-02-08   1.2045
2021-02-09   1.2106
2021-02-10   1.2132
2021-02-11   1.2127
2021-02-12   1.2126
2021-02-15      NaN
2021-02-16   1.2107
2021-02-17   1.2042
2021-02-18   1.2078
2021-02-19   1.2136
2021-02-22   1.2155
2021-02-23   1.2142
2021-02-24   1.2143
2021-02-25   1.2229
2021-02-26   1.2093
2021-03-01   1.2054
2021-03-02   1.2079
2021-03-03   1.2073
2021-03-04   1.2045
2021-03-05   1.1914
2021-03-08   1.1849
2021-03-09   1.1885
2021-03-10   1.1900
2021-03-11   1.1978
````

Note the NaN on 2-15, which corresponds to President's Day.