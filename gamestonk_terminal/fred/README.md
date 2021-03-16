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

The GDP is specifically defined in this menu, but to reproduce it with the custom function, it would be
````
cust -id GDP -s 2020-01-01 -p True 
````

The plot flag allows for plotting and the disp flag tells whether to print data to the console.