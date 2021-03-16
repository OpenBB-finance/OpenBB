# fred

The purpose of fred is to have the ability to look at economic data.

* [GDP](#GDP)
    * Get GDP data
* [cust](#cust)
    * Get custom fred data  

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


## cust <a name="cust"></a>

The fred database has many different datasets freely available.  They each have their own custom SERIES_ID which can be obtained through the website.

````
usage: cust [-id] [-s START_DATE] [-p PLOT] [-disp DISP]
````
* -id : Series ID for FRED data.  Required argument
* -s : Start data to acquire data.  Defaults to 1/1/2020
* -p : Option to plot. Defaults to False
* -disp : Option to print data to console.  Defaults to True.

The GDP is specifically defined in this menu, but to reproduce it with the custom function, it would be
````
cust -id GDP -s 1/1/2020 -p True -disp False
````

The plot flag allows for plotting and the disp flag tells whether or not to print data to the console.