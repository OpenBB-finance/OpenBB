---
title: Economy
---

The Economy module wraps the functions from the Economy menu of the OpenBB Terminal, and provides the user with more control over their workflow. In a Jupyter Notebook environment, it is quick and easy to get going. To get the most out of these functions, it is highly recommended to acquire API keys for:

- [FRED](https://fred.stlouisfed.org)
- [Quandl/Nasdaq Data Link](https://data.nasdaq.com)
- [AlphaVantage](https://www.alphavantage.co/)

Define the keys for the OpenBB installation with:

```python

openbb.keys.fred(key = 'REPLACE_ME', persist = True)
openbb.keys.quandl(key = 'REPLACE_ME', persist = True)
openbb.keys.av(key = 'REPLACE_ME', persist = True)
```

## How to Use

Below is brief description of each function within the Economy module:

| Path                                |    Type    |                                                    Description |
| :---------------------------------- | :--------: | -------------------------------------------------------------: |
| openbb.economy.available_indices    | Dictionary |                                 Curated List of Global Indices |
| openbb.economy.bigmac               |  Function  |                                              The Big Mac Index |
| openbb.economy.bigmac_chart         |  Function  |                                             Chart for `bigmac` |
| openbb.economy.country_codes        |  Function  |                         List of Three-Letter ISO Country Codes |
| openbb.economy.cpi                  |  Function  |                               Monthly US CPI from AlphaVantage |
| openbb.economy.cpi_chart            |  Function  |                                                Chart for `cpi` |
| openbb.economy.currencies           |  Function  |                                            Currencies from WSJ |
| openbb.economy.events               |  Function  |                                              Economic Calendar |
| openbb.economy.fred_ids             |  Function  |                         Search for a FRED series ID by keyword |
| openbb.economy.fred_notes           |  Function  |                       Search by Keyword for Series Information |
| openbb.economy.futures              |  Function  |                                  Current Prices of Commodities |
| openbb.economy.gdpc                 |  Function  |                            US GDP per Capita from AlphaVantage |
| openbb.economy.gdpc_chart           |  Function  |                                               Chart for `gdpc` |
| openbb.economy.get_events_countries |    List    |                          List of Countries for Events Function |
| openbb.economy.get_groups           |    List    |         List of Groups for Performance and Valuation Functions |
| openbb.economy.glbonds              |  Function  |               Table of Select 10 Year Sovereign Bonds from WSJ |
| openbb.economy.indices              |  Function  |                                        Top US Indices from WSJ |
| openbb.economy.index                |  Function  |            Historical Daily Data for Indices from YahooFinance |
| openbb.economy.index_chart          |  Function  |                                              Chart for `index` |
| openbb.economy.inf                  |  Function  |                          US Inflation Prints from AlphaVantage |
| openbb.economy.inf_chart            |  Function  |                                                Chart for `inf` |
| openbb.economy.macro                |  Function  |                                   Gets Series Data from EconDB |
| openbb.economy.macro_chart          |  Function  |                                              Chart for `macro` |
| openbb.economy.macro_countries      |    List    |                   List of Countries Accepted by Macro Function |
| openbb.economy.macro_parameters     | Dictionary |     Dictionary of Parameters & Descriptions for Macro Function |
| openbb.economy.overview             |  Function  |                               General Market Overview from WSJ |
| openbb.economy.perfmap              |  Function  |                 Opens a Browser to Performance Map from Finviz |
| openbb.economy.performance          |  Function  |                                  Performance Data (get_groups) |
| openbb.economy.rtps                 |  Function  | Real-Time Performance by Sector (US Markets) from AlphaVantage |
| openbb.economy.rtps_chart           |  Function  |                                                Chart of `rtps` |
| openbb.economy.search_index         |  Function  |                              Search for a Global Index by Name |
| openbb.economy.treasury             |  Function  |                                             US Treasuries Data |
| openbb.economy.treasury_chart       |  Function  |                                           Chart for `treasury` |
| openbb.economy.treasury_maturities  |  Function  | Table of Accepted Values for Maturities Argument in `treasury` |
| openbb.economy.tyld                 |  Function  |                   Historical Treasury Yields from AlphaVantage |
| openbb.economy.tyld_chart           |  Function  |                                                Chart of `tyld` |
| openbb.economy.unemp                |  Function  |              Historical US Unemployment Data from AlphaVantage |
| openbb.economy.unemp_chart          |  Function  |                                               Chart of `unemp` |
| openbb.economy.usbonds              |  Function  |                 Table of Current Rate, Yield, and Yield Change |
| openbb.economy.valuation            |  Function  |                          Valuation for Group from (get_gropus) |
| openbb.economy.ycrv                 |  Function  |           Current and Historical US Yield Curve Data from FRED |
| openbb.economy.ycrv_chart           |  Function  |                                               Chart for `ycrv` |

Alternatively, the contents of the economy, or function docstrings, is printed with:

```python
help(openbb.economy)
```

## Examples

### Import Statements

The examples will assume that this code block is included with the import statements:

```python
from openbb_terminal.sdk import openbb
import pandas as pd
%matplotlib inline
```

### Index

The `index` function can request data using a couple of methods. There is a curated list of global indexes which can be entered by symbol or values from the left column of the table below.

```python
indexes = pd.DataFrame.from_dict(openbb.economy.available_indices()).transpose()

indexes
```

|           | name                            | ticker   |
| :-------- | :------------------------------ | :------- |
| sp500     | S&P 500 Index                   | ^GSPC    |
| sp400     | S&P 400 Mid Cap Index           | ^SP400   |
| sp600     | S&P 600 Small Cap Index         | ^SP600   |
| sp500tr   | S&P 500 TR Index                | ^SP500TR |
| sp_xsp    | S&P 500 Mini SPX Options Index  | ^XSP     |
| cboe_tyx  | CBOE 30 year Treasury Yields    | ^TYX     |
| cboe_irx  | CBOE 13 Week Treasury Bill      | ^IRX     |
| move      | ICE BofAML Move Index           | ^MOVE    |
| dxy       | US Dollar Index                 | DX-Y.NYB |
| crypto200 | CMC Crypto 200 Index by Solacti | ^CMC200  |

This list can be filtered:

```python
indexes.filter(like = 'sp_', axis = 0)
```

|                          | name                                               | ticker        |
| :----------------------- | :------------------------------------------------- | :------------ |
| sp_xsp                   | S&P 500 Mini SPX Options Index                     | ^XSP          |
| sp_energy_ig             | S&P 500 Energy (Industry Group) Index              | ^SP500-1010   |
| sp_energy_equipment      | S&P 500 Energy Equipment & Services Industry Index | ^SP500-101010 |
| sp_energy_oil            | S&P 500 Oil, Gas & Consumable Fuels Industry Index | ^SP500-101020 |
| sp_materials_sector      | S&P 500 Materials Sector Index                     | ^SP500-15     |
| sp_utilities_sector      | S&P 500 Utilities Sector Index                     | ^SP500-55     |
| sp_utilities_electricity | S&P 500 Electric Utilities Index                   | ^SP500-551010 |
| sp_utilities_multis      | S&P 500 Multi-Utilities Industry Index             | ^SP500-551030 |
| sp_re_sector             | S&P 500 Real Estate Sector Index                   | ^SP500-60     |
| sp_re_ig                 | S&P 500 Real Estate (Industry Group) Index         | ^SP500-6010   |

One index, or multiple, can be requested as a single DataFrame:

```python
df = openbb.economy.index(indices = ['sp_energy_oil', 'sp_energy_equipment', 'sp_energy_ig'])

df.tail(3)
```

| Date                | sp_energy_oil | sp_energy_equipment | sp_energy_ig |
| :------------------ | ------------: | ------------------: | -----------: |
| 2022-11-14 00:00:00 |        800.76 |              330.53 |       712.28 |
| 2022-11-15 00:00:00 |        809.27 |              335.84 |       720.16 |
| 2022-11-16 00:00:00 |        792.32 |              326.49 |       704.68 |

This can also be displayed as a chart:

```python
openbb.economy.index_chart(indices = ['sp_energy_oil', 'sp_energy_equipment', 'sp_energy_ig'])
```

![openbb.economy.index_chart](https://user-images.githubusercontent.com/85772166/202557572-b67f35e1-a17a-4724-83b3-1b1175e0445d.png "openbb.economy.index_chart")

### Performance

Performance metrics for sectors, industries, and regions (US listed) are printed with:

```python
openbb.economy.performance(group = 'energy')
```

|     | Name                           |    Week |  Month |  3Month | 6Month |   1Year |    YTD | Recom | AvgVolume [1M] | RelVolume |  Change | Volume [1M] |
| --: | :----------------------------- | ------: | -----: | ------: | -----: | ------: | -----: | ----: | -------------: | --------: | ------: | ----------: |
|   0 | Oil & Gas Drilling             |  0.0106 | 0.2154 |  0.2501 | 0.1534 |   0.711 | 0.8991 |  1.92 |          33.58 |      0.71 |  -0.013 |       16.93 |
|   1 | Oil & Gas E&P                  |  0.0019 | 0.0618 |  0.1188 |   0.15 |  0.6602 | 0.6922 |  2.18 |         287.09 |      0.66 | -0.0059 |      136.36 |
|   2 | Oil & Gas Equipment & Services | -0.0063 | 0.1613 |   0.305 | 0.1219 |   0.493 | 0.5702 |   2.1 |           74.1 |      0.52 | -0.0125 |       27.79 |
|   3 | Oil & Gas Integrated           |  0.0166 | 0.0557 |  0.0885 | 0.0462 |  0.4014 | 0.4114 |  2.23 |         122.44 |      0.71 | -0.0079 |       62.12 |
|   4 | Oil & Gas Midstream            | -0.0113 |  0.038 |  -0.019 | 0.0045 |  0.1551 | 0.2027 |   2.3 |         105.55 |      0.65 | -0.0115 |        48.8 |
|   5 | Oil & Gas Refining & Marketing |  0.0147 | 0.0929 |  0.1562 | 0.1585 |  0.6038 | 0.6084 |  2.13 |          30.59 |      0.61 | -0.0006 |       13.32 |
|   6 | Thermal Coal                   | -0.0096 | 0.0291 | -0.0494 | 0.1289 |  1.2305 | 1.0504 |  1.97 |           8.74 |      0.69 | -0.0207 |        4.28 |
|   7 | Uranium                        | -0.0176 | 0.0416 |  0.0856 | 0.0426 | -0.1746 | 0.0267 |  1.61 |          32.44 |      0.54 | -0.0125 |       12.58 |

Performance by sector:

```python
openbb.economy.performance(group = 'sector')
```

|     | Name                   |    Week |  Month |  3Month |  6Month |   1Year |     YTD | Recom | AvgVolume [1M] | RelVolume |  Change | Volume [1M] |
| --: | :--------------------- | ------: | -----: | ------: | ------: | ------: | ------: | ----: | -------------: | --------: | ------: | ----------: |
|   0 | Basic Materials        | -0.0032 |  0.129 |  0.0195 | -0.0572 | -0.0684 | -0.0928 |  2.22 |         469.94 |      0.66 | -0.0116 |       222.2 |
|   1 | Communication Services |  0.0343 | 0.0128 | -0.1444 | -0.1297 | -0.3837 | -0.3529 |  1.97 |         731.34 |      0.72 |  0.0004 |      377.12 |
|   2 | Consumer Cyclical      |  0.0111 | 0.0266 | -0.1386 | -0.0182 | -0.3665 | -0.3221 |  2.14 |           1430 |      1.01 | -0.0034 |        1040 |
|   3 | Consumer Defensive     |   0.003 | 0.0757 | -0.0302 |  0.0573 |  -0.019 | -0.0574 |  2.31 |         298.74 |      0.85 | -0.0019 |      181.95 |
|   4 | Energy                 |  0.0067 | 0.0629 |  0.0913 |  0.0736 |  0.4208 |  0.4497 |  2.21 |         694.52 |      0.65 |  -0.008 |      322.19 |
|   5 | Financial              | -0.0095 | 0.0934 | -0.0098 |  0.0339 | -0.1259 | -0.1137 |  2.24 |         861.74 |      0.79 |  -0.005 |      489.78 |
|   6 | Healthcare             | -0.0121 | 0.0703 | -0.0125 |  0.0177 | -0.1074 | -0.1161 |  2.11 |           1180 |      0.87 |  0.0002 |      736.58 |
|   7 | Industrials            | -0.0118 | 0.0969 | -0.0223 |  0.0723 | -0.1138 |  -0.101 |  2.32 |         573.08 |       0.7 |  -0.005 |      285.24 |
|   8 | Real Estate            | -0.0259 | 0.0884 | -0.1441 | -0.0961 | -0.2413 | -0.2738 |  2.18 |         341.84 |      0.55 | -0.0055 |      134.66 |
|   9 | Technology             |  0.0149 | 0.0938 | -0.1095 | -0.0044 | -0.3024 | -0.2957 |  2.03 |           1460 |      0.86 |  0.0039 |      904.44 |
|  10 | Utilities              | -0.0235 | 0.0485 | -0.1212 | -0.0582 | -0.0054 | -0.0569 |  2.29 |         166.21 |      0.67 | -0.0142 |       79.25 |

### Events

A global economic calendar is accessible through the `events` function:

```python
help(openbb.economy.events)

Help on Operation in module openbb_terminal.core.library.operation:

<openbb_terminal.core.library.operation.Operation object>
    Get economic calendar for countries between specified dates

    Parameters
    ----------
    countries : [List[str],str]
        List of countries to include in calendar.  Empty returns all
    start_date : str
        Start date for calendar
    end_date : str
        End date for calendar

    Returns
    -------
    pd.DataFrame
        Economic calendar
```

With no arguments, `events` will return the calendar from today:

```python
openbb.economy.events()
```

|     | Time (GMT) | Country        | Event                    | actual | consensus | previous | Date       |
| --: | :--------- | :------------- | :----------------------- | :----- | :-------- | :------- | :--------- |
|   0 | 02:00      | United Kingdom | Car Registration         | -40.4% | -         | 227.2%   | 2022-11-17 |
|   1 | 02:00      | United Kingdom | Car Registration         | 26.4%  | -         | 4.6%     | 2022-11-17 |
|   2 | 02:00      | Italy          | Italian Car Registration | 14.6%  | -         | 5.4%     | 2022-11-17 |
|   3 | 02:00      | Italy          | Italian Car Registration | 4.4%   | -         | 55.9%    | 2022-11-17 |
|   4 | 02:00      | Switzerland    | Trade Balance            | 4.140B | -         | 4.193B   | 2022-11-17 |
|  56 | 13:00      | United States  | 10-Year TIPS Auction     | 1.485% | -         | 1.248%   | 2022-11-17 |
|  57 | 18:30      | Japan          | CPI, n.s.a               | -      | -         | 0.4%     | 2022-11-17 |
|  58 | 18:30      | Japan          | National Core CPI        | -      | 3.5%      | 3.0%     | 2022-11-17 |
|  59 | 18:30      | Japan          | National CPI             | -      | -         | 3.0%     | 2022-11-17 |
|  60 | 19:01      | United Kingdom | GfK Consumer Confidence  | -      | -52       | -47      | 2022-11-17 |

Calendar events can be requested for a specific countries and date ranges:

```python
openbb.economy.events(countries = ['United States'], start_date = '2022-11-18', end_date = '2022-11-18')
```

|     | Time (GMT) | Country       | Event                             | actual | consensus | previous | Date       |
| --: | :--------- | :------------ | :-------------------------------- | :----- | :-------- | :------- | :--------- |
|   0 | 10:00      | United States | Existing Home Sales               | -      | 4.38M     | 4.71M    | 2022-11-18 |
|   1 | 10:00      | United States | Existing Home Sales               | -      | -         | -1.5%    | 2022-11-18 |
|   2 | 10:00      | United States | US Leading Index                  | -      | -0.4%     | -0.4%    | 2022-11-18 |
|   3 | 13:00      | United States | U.S. Baker Hughes Oil Rig Count   | -      | -         | 622      | 2022-11-18 |
|   4 | 13:00      | United States | U.S. Baker Hughes Total Rig Count | -      | -         | 779      | 2022-11-18 |

### FRED

Search the FRED database for a series titles containing keywords:

```python
series_ids = openbb.economy.fred_ids(search_query = 'Oil and Gas')

series_ids.head(5)
```

| id              | title                                                                                               |
| :-------------- | :-------------------------------------------------------------------------------------------------- |
| PCU333132333132 | Producer Price Index by Industry: Oil and Gas Field Machinery and Equipment Manufacturing           |
| CES1021100001   | All Employees, Oil and Gas Extraction                                                               |
| IPG211111CS     | Industrial Production: Mining, Quarrying, and Oil and Gas Extraction: Crude Oil (NAICS = 211111pt.) |
| A33DNO          | Manufacturers' New Orders: Mining, Oil, and Gas Field Machinery Manufacturing                       |
| PCU21112111     | Producer Price Index by Industry: Oil and Gas Extraction                                            |

### Macro

The `macro` function will return a Tuple. See refer to the docstring below to see the input arguments:

```python
help(openbb.economy.macro)

Help on Operation in module openbb_terminal.core.library.operation:

<openbb_terminal.core.library.operation.Operation object>
    Use 'economy.macro_chart' to access the view.
    This functions groups the data queried from the EconDB database [Source: EconDB]

        Parameters
        ----------
        parameters: list
            The type of data you wish to download. Available parameters can be accessed through economy.macro_parameters().
        countries : list
            The selected country or countries. Available countries can be accessed through economy.macro_countries().
        transform : str
            The selected transform. Available transforms can be accessed through get_macro_transform().
        start_date : str
            The starting date, format "YEAR-MONTH-DAY", i.e. 2010-12-31.
        end_date : str
            The end date, format "YEAR-MONTH-DAY", i.e. 2020-06-05.
        symbol : str
            In what currency you wish to convert all values.

        Returns
        -------
        Tuple[pd.DataFrame, Dict[Any, Dict[Any, Any]], str]
            A DataFrame with the requested macro data of all chosen countries,
            A dictionary containing the units of each country's parameter (e.g. EUR),
            A string denomination which can be Trillions, Billions, Millions, Thousands

        Examples
        --------
        >>> from openbb_terminal.sdk import openbb
        >>> macro_df = openbb.economy.macro()
```

`openbb.economy.macro_parameters()` will return a list of dictionaries. Read it as a DataFrame with:

```python
parameters = pd.DataFrame.from_dict(openbb.economy.macro_parameters()).transpose()

parameters.tail(5)
```

|         | name                      | period  | description                                                                                                                          |
| :------ | :------------------------ | :------ | :----------------------------------------------------------------------------------------------------------------------------------- |
| Y10YD   | Long term yield (10-year) | Monthly | The 10-year yield is used as a proxy for mortgage rates. It's also seen as a sign of investor sentiment about the country's economy. |
| M3YD    | 3 month yield             | Monthly | The yield received for investing in a government issued treasury security that has a maturity of 3 months                            |
| HOU     | House price index         | Monthly | House price index defined with base 2015 for Europe with varying bases for others. See: https://www.econdb.com/main-indicators       |
| OILPROD | Oil production            | Monthly | The amount of oil barrels produced per day in a month within a country.                                                              |
| POP     | Population                | Monthly | The population of a country. This can be in thousands or, when relatively small, in actual units.                                    |

The data from the `macro` function is unpacked like:

```python
data,units,denomination = openbb.economy.macro(parameters = ['Y10YD'], countries = ['United States', 'Poland', 'France', 'Italy', 'Spain', 'Germany'])

data.tail(10)
```

| date                | France | Germany | Italy | Poland | Spain | United States |
| :------------------ | -----: | ------: | ----: | -----: | ----: | ------------: |
| 2022-01-01 00:00:00 |   0.31 |   -0.12 |  1.35 |      4 |  0.66 |          1.76 |
| 2022-02-01 00:00:00 |   0.68 |    0.15 |  1.79 |   3.95 |  1.11 |          1.93 |
| 2022-03-01 00:00:00 |   0.78 |    0.28 |  1.85 |   4.83 |  1.22 |          2.13 |
| 2022-04-01 00:00:00 |   1.28 |    0.75 |  2.44 |   5.96 |  1.69 |          2.75 |
| 2022-05-01 00:00:00 |   1.52 |    0.95 |  2.99 |   6.64 |  2.04 |           2.9 |
| 2022-06-01 00:00:00 |   2.06 |    1.45 |  3.64 |   7.14 |  2.63 |          3.14 |
| 2022-07-01 00:00:00 |   1.71 |    1.08 |  3.36 |   6.37 |  2.31 |           2.9 |
| 2022-08-01 00:00:00 |   1.69 |    1.03 |   3.3 |    5.8 |  2.15 |           2.9 |
| 2022-09-01 00:00:00 |   2.41 |     1.8 |  4.14 |   6.28 |  2.92 |          3.52 |
| 2022-10-01 00:00:00 |   2.77 |    2.19 |  4.53 |   7.82 |  3.29 |          3.98 |
