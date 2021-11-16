```
usage: bigmac [-c COUNTRIES] [--raw] [-h] [--export {png,jpg,pdf,svg}]
```
The notion that in the long run exchange rates should move towards the rate that would equalise the prices of an identical basket of goods and services (in this case, a burger) in any two countries. Burgernomics was never intended as a precise gauge of currency misalignment, merely a tool to make exchange-rate theory more digestible. Yet the Big Mac index has become a global standard, included in several economic textbooks and the subject of dozens of academic studies.

Big Mac prices are from McDonald’s directly and from reporting around the world; exchange rates are from Thomson Reuters; GDP and population data used to calculate the euro area averages are from Eurostat and GDP per person data are from the IMF World Economic Outlook reports.

The Big Mac PPP exchange rate between two countries is obtained by dividing the price of a Big Mac in one country (in its currency) by the price of a Big Mac in another country (in its currency).

Source: https://data.nasdaq.com/data/ECONOMIST-the-economist-big-mac-index

List of country codes for this feature: https://static.quandl.com/ECONOMIST_Descriptions/economist_country_codes.csv

```
optional arguments:
  -c COUNTRIES, --countries COUNTRIES
                        Country codes to get data for. (default: USA)
  --raw                 Show raw data (default: False)
  -h, --help            show this help message (default: False)
  --export {png,jpg,pdf,svg}
                        Export or figure into png, jpg, pdf, svg (default: )
```

Sample usage, which gets the index for 7 different countries:

```
bigmac -c USA,EUR,MEX,CAN,UAE,RUS
```
<img size="1400" alt="Big Mac Index" src="https://user-images.githubusercontent.com/18151143/141603738-ffa86906-4e1e-48b4-97b8-ed51f1806089.png">
     
