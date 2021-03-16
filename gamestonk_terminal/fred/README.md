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
* -s : Start Date.  Format m/d/y. First point to get
* -p : Option to plot.  Defaults to False

To get and plot the last 20 reported GDP values:
````
gdp -n 20 
````
To show all GDP data since 1/1/2010, with no plot.
````
gdp -s 1/1/2010 -p True
````


## cust <a name="cust"></a>

The fred database has many different datasets freely available.  They each have their own custom SERIES_ID which can be obtained through the website.

````
usage: cust [-id] [-s START_DATE] [-p PLOT] [-disp DISP]
````
* -id : Series ID for FRED data.  Required argument
* -s : Start data to acquire data.  Defaults to 1/1/2020
* -p : Option to plot. Defaults to True
* -disp : Option to print data to console.  Defaults to False.

The GDP is specifically defined in this menu, but to reproduce it with the custom function, it would be
````
cust -id GDP -s 1/1/2020 -p True 
````

The plot flag allows for plotting and the disp flag tells whether to print data to the console.