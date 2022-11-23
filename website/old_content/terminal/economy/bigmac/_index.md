```
usage: bigmac [--codes] [-c COUNTRIES] [-h] [--export {csv,json,xlsx,png,jpg,pdf,svg}] [--raw]
```
The notion that in the long run exchange rates should move towards the rate that would equalise the prices of an identical basket of goods and services (in this case, a burger) in any two countries. Burgernomics was never intended as a precise gauge of currency misalignment, merely a tool to make exchange-rate theory more digestible. Yet the Big Mac index has become a global standard, included in several economic textbooks and the subject of dozens of academic studies.

Big Mac prices are from McDonald’s directly and from reporting around the world; exchange rates are from Thomson Reuters; GDP and population data used to calculate the euro area averages are from Eurostat and GDP per person data are from the IMF World Economic Outlook reports.

The Big Mac PPP exchange rate between two countries is obtained by dividing the price of a Big Mac in one country (in its currency) by the price of a Big Mac in another country (in its currency).

Source of the data can be found [here](https://data.nasdaq.com/data/ECONOMIST-the-economist-big-mac-index) and a list of country codes for this feature can be found [here](https://static.quandl.com/ECONOMIST_Descriptions/economist_country_codes.csv).

```
optional arguments:
  --codes               Flag to show all country codes (default: False)
  -c COUNTRIES, --countries COUNTRIES
                        Country codes to get data for. (default: USA)
  -h, --help            show this help message (default: False)
  --export {csv,json,xlsx,png,jpg,pdf,svg}
                        Export raw data into csv, json, xlsx and figure into png, jpg, pdf, svg (default: )
  --raw                 Flag to display raw data (default: False)
```

Sample usage, which gets the index for 5 different countries:

```
bigmac -c USA,EUR,MEX,CAN,RUS
```
![bigmac](https://user-images.githubusercontent.com/46355364/158362967-8353fa50-2eb1-43b0-9cbb-bc3c3aec2e2a.png)

     
