# FRED

The purpose of fred is to have the ability to look at economic data.

* [gdp](#gdp)
    * Get GDP data
* [cust](#cust)
    * Get custom fred data  

## gdp <a name="gdp"></a>
```text
usage: gdp [-n N_TO_GET] [-s START_DATE] [-p PLOT]]
```
Gets GDP data.  Data is released quarterly
* -n : Number of points to display.  If unspecified, it will display all available.
* -s : Start Date.  Format YYYY-mm-dd. First point to get.  Defaults to Jan 1 2015
* -p : Option to plot.  Defaults to False

To get and plot the last 20 reported GDP values:
````
gdp -n 20 
````
To show all GDP data since 1/1/2016, with no plot.
````
gdp -s 2016-01-01 -p False
````
````
Date: 01-01-2015, GDP: 18003.399 
Date: 04-01-2015, GDP: 18223.577 
Date: 07-01-2015, GDP: 18347.425 
Date: 10-01-2015, GDP: 18378.803 
Date: 01-01-2016, GDP: 18470.156 
Date: 04-01-2016, GDP: 18656.207 
Date: 07-01-2016, GDP: 18821.359 
Date: 10-01-2016, GDP: 19032.58 
Date: 01-01-2017, GDP: 19237.435 
Date: 04-01-2017, GDP: 19379.232 
Date: 07-01-2017, GDP: 19617.288 
Date: 10-01-2017, GDP: 19937.963 
Date: 01-01-2018, GDP: 20242.215 
Date: 04-01-2018, GDP: 20552.653 
Date: 07-01-2018, GDP: 20742.723 
Date: 10-01-2018, GDP: 20909.853 
Date: 01-01-2019, GDP: 21115.309 
Date: 04-01-2019, GDP: 21329.877 
Date: 07-01-2019, GDP: 21540.325 
Date: 10-01-2019, GDP: 21747.394 
Date: 01-01-2020, GDP: 21561.139 
Date: 04-01-2020, GDP: 19520.114 
Date: 07-01-2020, GDP: 21170.252 
Date: 10-01-2020, GDP: 21487.896 

````


## cust <a name="cust"></a>

The fred database has many different datasets freely available.  They each have their own custom SERIES_ID which can be obtained through the website.

````
usage: cust [-id] [-s START_DATE] [-p PLOT] [-disp DISP]
````
* -id : Series ID for FRED data.  Required argument
* -s : Start Date.  Format YYYY-mm-dd. First point to get.  Defaults to Jan 1 2015.
* -p : Option to plot. Defaults to True
* -disp : Option to print data to console.  Defaults to False.

An example of custom data could be the unemployment rate.  According to https://fred.stlouisfed.org/series/UNRATE , the series ID is UNRATE.  So to plot this for 2019 to now

````
cust -id UNRATE -s 2019-01-01 -disp True
````
This will plot and display:


````
Date: 01-01-2019, DATA: 4.0 
Date: 02-01-2019, DATA: 3.8 
Date: 03-01-2019, DATA: 3.8 
Date: 04-01-2019, DATA: 3.7 
Date: 05-01-2019, DATA: 3.7 
Date: 06-01-2019, DATA: 3.6 
Date: 07-01-2019, DATA: 3.6 
Date: 08-01-2019, DATA: 3.7 
Date: 09-01-2019, DATA: 3.5 
Date: 10-01-2019, DATA: 3.6 
Date: 11-01-2019, DATA: 3.6 
Date: 12-01-2019, DATA: 3.6 
Date: 01-01-2020, DATA: 3.5 
Date: 02-01-2020, DATA: 3.5 
Date: 03-01-2020, DATA: 4.4 
Date: 04-01-2020, DATA: 14.8 
Date: 05-01-2020, DATA: 13.3 
Date: 06-01-2020, DATA: 11.1 
Date: 07-01-2020, DATA: 10.2 
Date: 08-01-2020, DATA: 8.4 
Date: 09-01-2020, DATA: 7.8 
Date: 10-01-2020, DATA: 6.9 
Date: 11-01-2020, DATA: 6.7 
Date: 12-01-2020, DATA: 6.7 
Date: 01-01-2021, DATA: 6.3 
Date: 02-01-2021, DATA: 6.2 
````