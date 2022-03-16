```
usage: macro [-p PARAMETERS [PARAMETERS ...]] [-c COUNTRIES [COUNTRIES ...]] [-sp] [-sc] [-s START_DATE] [-e END_DATE] [-cc CONVERT_CURRENCY] [-st] [-h] [--export {csv,json,xlsx}] [--raw]
```

Get a broad selection of macro data from one or multiple countries. This includes Gross Domestic Product (RGDP & GDP) and the underlying components, Treasury Yields (Y10YD & M3YD), Employment figures (URATE, EMP, AC0I0 and EMRATIO),
Government components (e.g. GBAL & GREV), Consumer and Producer Indices (CPI & PPI) and a variety of other indicators. [Source: EconDB]

```
optional arguments:
  -p PARAMETERS [PARAMETERS ...], --parameters PARAMETERS [PARAMETERS ...]
                        Abbreviation(s) of the Macro Economic data (default: ['CPI'])
  -c COUNTRIES [COUNTRIES ...], --countries COUNTRIES [COUNTRIES ...]
                        The country or countries you wish to show data for (default: ['United_States'])
  -sp, --show_parameters
                        Show all parameters and what they represent (default: False)
  -sc, --show_countries
                        Show all countries and their currencies (default: False)
  -s START_DATE, --start_date START_DATE
                        The start date of the data (format: YEAR-MONTH-DAY, i.e. 2010-12-31) (default: None)
  -e END_DATE, --end_date END_DATE
                        The end date of the data (format: YEAR-MONTH-DAY, i.e. 2021-06-20) (default: None)
  -cc CONVERT_CURRENCY, --convert_currency CONVERT_CURRENCY
                        Convert the currency of the chosen country to a specified currency. To find the currency symbols use the argument -sc (default: False)
  -st, --store          Store the data to be used for plotting with the 'plot' command. (default: False)
  -h, --help            show this help message (default: False)
  --export {csv,json,xlsx}
                        Export raw data into csv, json, xlsx (default: )
  --raw                 Flag to display raw data (default: False)
```

Example:
```
2022 Mar 15, 07:20 (✨) /economy/ $ macro -p CONF -c Netherlands Germany France -s 2005-01-01 -e 2022-01-01
```
![macro conf netherlands germany france](https://user-images.githubusercontent.com/46355364/158573827-e517ead4-f304-4807-963d-cd884f76f132.png)

```
2022 Mar 15, 07:22 (✨) /economy/ $ macro -p OILPROD -c Canada United_States -cc USD -s 2004-01-01
```
![oil production macro](https://user-images.githubusercontent.com/46355364/158573994-a75efcfc-ccda-484e-80a8-b7df4ab96d57.png)

```
2022 Mar 16, 06:52 (✨) /economy/ $ macro -sp
┏━━━━━━━━━━━┳━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┳━━━━━━━━━━━━┳━━━━━━━━━━━┳━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓
┃ Parameter ┃ Name                                                ┃ Scale      ┃ Period    ┃ Description                                                                                                                                    ┃
┡━━━━━━━━━━━╇━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━╇━━━━━━━━━━━━╇━━━━━━━━━━━╇━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┩
│ RGDP      │ Real gross domestic product                         │ Millions   │ Quarterly │ Inflation-adjusted measure that reflects the value of all goods and services produced by an economy in a given year (chain-linked series).     │
├───────────┼─────────────────────────────────────────────────────┼────────────┼───────────┼────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┤
│ RPRC      │ Real private consumption                            │ Millions   │ Quarterly │ All purchases made by consumers adjusted by inflation (chain-linked series).                                                                   │
├───────────┼─────────────────────────────────────────────────────┼────────────┼───────────┼────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┤
│ RPUC      │ Real public consumption                             │ Millions   │ Quarterly │ All purchases made by the government adjusted by inflation (chain-linked series).                                                              │
├───────────┼─────────────────────────────────────────────────────┼────────────┼───────────┼────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┤
│ RGFCF     │ Real gross fixed capital formation                  │ Millions   │ Quarterly │ The acquisition of produced assets adjusted by inflation (chain-linked series).                                                                │
├───────────┼─────────────────────────────────────────────────────┼────────────┼───────────┼────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┤
│ REXP      │ Real exports of goods and services                  │ Millions   │ Quarterly │ Transactions in goods and services from residents to non-residents adjusted for inflation (chain-linked series)                                │
├───────────┼─────────────────────────────────────────────────────┼────────────┼───────────┼────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┤
│ RIMP      │ Real imports of goods and services                  │ Millions   │ Quarterly │ Transactions in goods and services to residents from non-residents adjusted for inflation (chain-linked series)                                │
├───────────┼─────────────────────────────────────────────────────┼────────────┼───────────┼────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┤
│ GDP       │ Gross domestic product                              │ Millions   │ Quarterly │ Measure that reflects the value of all goods and services produced by an economy in a given year (chain-linked series).                        │
├───────────┼─────────────────────────────────────────────────────┼────────────┼───────────┼────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┤
│ PRC       │ Private consumption                                 │ Millions   │ Quarterly │ All purchases made by consumers (chain-linked series).                                                                                         │
├───────────┼─────────────────────────────────────────────────────┼────────────┼───────────┼────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┤
│ PUC       │ Public consumption                                  │ Millions   │ Quarterly │ All purchases made by the government (chain-linked series)                                                                                     │
├───────────┼─────────────────────────────────────────────────────┼────────────┼───────────┼────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┤
│ GFCF      │ Gross fixed capital formation                       │ Millions   │ Quarterly │ The acquisition of produced assets (chain-linked series).                                                                                      │
├───────────┼─────────────────────────────────────────────────────┼────────────┼───────────┼────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┤
│ EXP       │ Exports of goods and services                       │ Millions   │ Quarterly │ Transactions in goods and services from residents to non-residents (chain-linked series)                                                       │
├───────────┼─────────────────────────────────────────────────────┼────────────┼───────────┼────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┤
│ IMP       │ Imports of goods and services                       │ Millions   │ Quarterly │ Transactions in goods and services to residents from non-residents (chain-linked series)                                                       │
├───────────┼─────────────────────────────────────────────────────┼────────────┼───────────┼────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┤
│ CPI       │ Consumer price index                                │ Index      │ Monthly   │ Purchasing power defined with base 2015 for Europe with varying bases for others. See: https://www.econdb.com/main-indicators                  │
├───────────┼─────────────────────────────────────────────────────┼────────────┼───────────┼────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┤
│ PPI       │ Producer price index                                │ Index      │ Monthly   │ Change in selling prices with base 2015 for Europe with varying bases for others. See: https://www.econdb.com/main-indicators                  │
├───────────┼─────────────────────────────────────────────────────┼────────────┼───────────┼────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┤
│ CORE      │ Core consumer price index                           │ Index      │ Monthly   │ Purchasing power excluding food and energy defined with base 2015 for Europe with varying bases for others. See:                               │
│           │                                                     │            │           │ https://www.econdb.com/main-indicators                                                                                                         │
├───────────┼─────────────────────────────────────────────────────┼────────────┼───────────┼────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┤
│ URATE     │ Unemployment                                        │ Percentage │ Monthly   │ Monthly average % of the working-age population that is unemployed.                                                                            │
├───────────┼─────────────────────────────────────────────────────┼────────────┼───────────┼────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┤
│ EMP       │ Employment                                          │ Thousands  │ Quarterly │ The employed population within a country (in thousands).                                                                                       │
├───────────┼─────────────────────────────────────────────────────┼────────────┼───────────┼────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┤
│ ACOIO     │ Active population                                   │ Thousands  │ Quarterly │ The active population, unemployed and employed, in thousands.                                                                                  │
├───────────┼─────────────────────────────────────────────────────┼────────────┼───────────┼────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┤
│ EMRATIO   │ Employment to working age population                │ Percentage │ Quarterly │ Unlike the unemployment rate, the employment-to-population ratio includes unemployed people not looking for jobs.                              │
├───────────┼─────────────────────────────────────────────────────┼────────────┼───────────┼────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┤
│ RETA      │ Retail trade                                        │ Index      │ Monthly   │ Turnover of sales in wholesale and retail trade                                                                                                │
├───────────┼─────────────────────────────────────────────────────┼────────────┼───────────┼────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┤
│ CONF      │ Consumer confidence index                           │ Index      │ Monthly   │ Measures how optimistic or pessimistic consumers are regarding their expected financial situation.                                             │
├───────────┼─────────────────────────────────────────────────────┼────────────┼───────────┼────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┤
│ IP        │ Industrial production                               │ Index      │ Monthly   │ Measures monthly changes in the price-adjusted output of industry.                                                                             │
├───────────┼─────────────────────────────────────────────────────┼────────────┼───────────┼────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┤
│ CP        │ Construction production                             │ Index      │ Monthly   │ Measures monthly changes in the price-adjusted output of construction.                                                                         │
├───────────┼─────────────────────────────────────────────────────┼────────────┼───────────┼────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┤
│ GBAL      │ Government balance                                  │ Millions   │ Quarterly │ The government balance (or EMU balance) is the overall difference between government revenues and spending.                                    │
├───────────┼─────────────────────────────────────────────────────┼────────────┼───────────┼────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┤
│ GREV      │ General government total revenue                    │ Millions   │ Quarterly │ The total amount of revenues collected by governments is determined by past and current political decisions.                                   │
├───────────┼─────────────────────────────────────────────────────┼────────────┼───────────┼────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┤
│ GSPE      │ General government total expenditure                │ Millions   │ Quarterly │ Total expenditure consists of total expense and the net acquisition of non-financial assets.                                                   │
├───────────┼─────────────────────────────────────────────────────┼────────────┼───────────┼────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┤
│ GDEBT     │ Government debt                                     │ Millions   │ Quarterly │ The financial liabilities of the government.                                                                                                   │
├───────────┼─────────────────────────────────────────────────────┼────────────┼───────────┼────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┤
│ CA        │ Current account balance                             │ Millions   │ Monthly   │ A record of a country's international transactions with the rest of the world                                                                  │
├───────────┼─────────────────────────────────────────────────────┼────────────┼───────────┼────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┤
│ TBFR      │ Trade balance                                       │ Millions   │ Monthly   │ The difference between the monetary value of a nation's exports and imports over a certain time period.                                        │
├───────────┼─────────────────────────────────────────────────────┼────────────┼───────────┼────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┤
│ NIIP      │ Net international investment position               │ Millions   │ Quarterly │ Measures the gap between a nation's stock of foreign assets and a foreigner's stock of that nation's assets                                    │
├───────────┼─────────────────────────────────────────────────────┼────────────┼───────────┼────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┤
│ IIPA      │ Net international investment position (Assets)      │ Millions   │ Quarterly │ A nation's stock of foreign assets.                                                                                                            │
├───────────┼─────────────────────────────────────────────────────┼────────────┼───────────┼────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┤
│ IIPL      │ Net international investment position (Liabilities) │ Millions   │ Quarterly │ A foreigner's stock of the nation's assets.                                                                                                    │
├───────────┼─────────────────────────────────────────────────────┼────────────┼───────────┼────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┤
│ Y10YD     │ Long term yield (10-year)                           │ Percentage │ Monthly   │ The 10-year yield is used as a proxy for mortgage rates. It's also seen as a sign of investor sentiment about the country's economy.           │
├───────────┼─────────────────────────────────────────────────────┼────────────┼───────────┼────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┤
│ M3YD      │ 3 month yield                                       │ Percentage │ Monthly   │ The yield received for investing in a government issued treasury security that has a maturity of 3 months                                      │
├───────────┼─────────────────────────────────────────────────────┼────────────┼───────────┼────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┤
│ HOU       │ House price index                                   │ Index      │ Monthly   │ House price index defined with base 2015 for Europe with varying bases for others. See: https://www.econdb.com/main-indicators                 │
├───────────┼─────────────────────────────────────────────────────┼────────────┼───────────┼────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┤
│ OILPROD   │ Oil production                                      │ Thousands  │ Monthly   │ The amount of oil barrels produced per day in a month within a country.                                                                        │
├───────────┼─────────────────────────────────────────────────────┼────────────┼───────────┼────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┤
│ POP       │ Population                                          │ Thousands  │ Monthly   │ The population of a country. This can be in thousands or, when relatively small, in actual units.                                              │
└───────────┴─────────────────────────────────────────────────────┴────────────┴───────────┴────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┘
```
```
2022 Mar 15, 07:12 (✨) /economy/ $ macro -sc
┏━━━━━━━━━━━━━━━━━━━━━━━━┳━━━━━━━━━━┓
┃ Country                ┃ Currency ┃
┡━━━━━━━━━━━━━━━━━━━━━━━━╇━━━━━━━━━━┩
│ Albania                │ ALL      │
├────────────────────────┼──────────┤
│ Argentina              │ ARS      │
├────────────────────────┼──────────┤
│ Australia              │ AUD      │
├────────────────────────┼──────────┤
│ Austria                │ EUR      │
├────────────────────────┼──────────┤
│ Azerbaijan             │ AZN      │
├────────────────────────┼──────────┤
│ Bangladesh             │ BDT      │
├────────────────────────┼──────────┤
│ Belarus                │ BYR      │
├────────────────────────┼──────────┤
│ Belgium                │ EUR      │
├────────────────────────┼──────────┤
│ Bhutan                 │ BTN      │
├────────────────────────┼──────────┤
│ Bosnia_and_Herzegovina │ BAM      │
├────────────────────────┼──────────┤
│ Botswana               │ BWP      │
├────────────────────────┼──────────┤
│ Brazil                 │ BRL      │
├────────────────────────┼──────────┤
│ Bulgaria               │ BGN      │
├────────────────────────┼──────────┤
│ Cambodia               │ KHR      │
├────────────────────────┼──────────┤
│ Cameroon               │ XAF      │
├────────────────────────┼──────────┤
│ Canada                 │ CAD      │
├────────────────────────┼──────────┤
│ Chile                  │ CLP      │
├────────────────────────┼──────────┤
│ China                  │ CNY      │
├────────────────────────┼──────────┤
│ Colombia               │ COP      │
├────────────────────────┼──────────┤
│ Croatia                │ HRK      │
├────────────────────────┼──────────┤
│ Cyprus                 │ EUR      │
├────────────────────────┼──────────┤
│ Czech_Republic         │ CZK      │
├────────────────────────┼──────────┤
│ Denmark                │ DKK      │
├────────────────────────┼──────────┤
│ Dominican_Republic     │ DOP      │
├────────────────────────┼──────────┤
│ Egypt                  │ EGP      │
├────────────────────────┼──────────┤
│ Estonia                │ EUR      │
├────────────────────────┼──────────┤
│ Finland                │ EUR      │
├────────────────────────┼──────────┤
│ France                 │ EUR      │
├────────────────────────┼──────────┤
│ Germany                │ EUR      │
├────────────────────────┼──────────┤
│ Greece                 │ EUR      │
├────────────────────────┼──────────┤
│ Honduras               │ HNL      │
├────────────────────────┼──────────┤
│ Hong Kong              │ HKD      │
├────────────────────────┼──────────┤
│ Hungary                │ HUF      │
├────────────────────────┼──────────┤
│ India                  │ INR      │
├────────────────────────┼──────────┤
│ Indonesia              │ IDR      │
├────────────────────────┼──────────┤
│ Iran                   │ IRR      │
├────────────────────────┼──────────┤
│ Ireland                │ EUR      │
├────────────────────────┼──────────┤
│ Israel                 │ ILS      │
├────────────────────────┼──────────┤
│ Italy                  │ EUR      │
├────────────────────────┼──────────┤
│ Japan                  │ JPY      │
├────────────────────────┼──────────┤
│ Kazakhstan             │ KZT      │
├────────────────────────┼──────────┤
│ Laos                   │ LAK      │
├────────────────────────┼──────────┤
│ Latvia                 │ EUR      │
├────────────────────────┼──────────┤
│ Lebanon                │ LBP      │
├────────────────────────┼──────────┤
│ Lithuania              │ EUR      │
├────────────────────────┼──────────┤
│ Luxembourg             │ EUR      │
├────────────────────────┼──────────┤
│ Macedonia              │ MKD      │
├────────────────────────┼──────────┤
│ Malaysia               │ MYR      │
├────────────────────────┼──────────┤
│ Malta                  │ EUR      │
├────────────────────────┼──────────┤
│ Mexico                 │ MXN      │
├────────────────────────┼──────────┤
│ Mongolia               │ MNT      │
├────────────────────────┼──────────┤
│ Netherlands            │ EUR      │
├────────────────────────┼──────────┤
│ New_Zealand            │ NZD      │
├────────────────────────┼──────────┤
│ Nigeria                │ NGN      │
├────────────────────────┼──────────┤
│ Norway                 │ NOK      │
├────────────────────────┼──────────┤
│ Oman                   │ OMR      │
├────────────────────────┼──────────┤
│ Pakistan               │ PKR      │
├────────────────────────┼──────────┤
│ Panama                 │ PAB      │
├────────────────────────┼──────────┤
│ Peru                   │ PEN      │
├────────────────────────┼──────────┤
│ Philippines            │ PHP      │
├────────────────────────┼──────────┤
│ Poland                 │ PLN      │
├────────────────────────┼──────────┤
│ Portugal               │ EUR      │
├────────────────────────┼──────────┤
│ Qatar                  │ QAR      │
├────────────────────────┼──────────┤
│ Romania                │ RON      │
├────────────────────────┼──────────┤
│ Russia                 │ RUB      │
├────────────────────────┼──────────┤
│ Saudi_Arabia           │ SAR      │
├────────────────────────┼──────────┤
│ Serbia                 │ RSD      │
├────────────────────────┼──────────┤
│ Singapore              │ SGD      │
├────────────────────────┼──────────┤
│ Slovakia               │ EUR      │
├────────────────────────┼──────────┤
│ Slovenia               │ EUR      │
├────────────────────────┼──────────┤
│ South_Africa           │ ZAR      │
├────────────────────────┼──────────┤
│ South_Korea            │ KRW      │
├────────────────────────┼──────────┤
│ Spain                  │ EUR      │
├────────────────────────┼──────────┤
│ Sweden                 │ SEK      │
├────────────────────────┼──────────┤
│ Switzerland            │ CHF      │
├────────────────────────┼──────────┤
│ Taiwan                 │ TWD      │
├────────────────────────┼──────────┤
│ Thailand               │ THB      │
├────────────────────────┼──────────┤
│ Tunisia                │ TND      │
├────────────────────────┼──────────┤
│ Turkey                 │ TRY      │
├────────────────────────┼──────────┤
│ Ukraine                │ UAH      │
├────────────────────────┼──────────┤
│ United_Arab_Emirates   │ AED      │
├────────────────────────┼──────────┤
│ United_States          │ USD      │
├────────────────────────┼──────────┤
│ Uzbekistan             │ UZS      │
├────────────────────────┼──────────┤
│ Venezuela              │ VEF      │
├────────────────────────┼──────────┤
│ Vietnam                │ VND      │
└────────────────────────┴──────────┘
```
