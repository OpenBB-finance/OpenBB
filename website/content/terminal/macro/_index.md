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
![consumer confidence macro](https://user-images.githubusercontent.com/46355364/158367249-4b001139-1231-4140-9dba-70afd53a78e6.png)

```
2022 Mar 15, 07:22 (✨) /economy/ $ macro -p OILPROD -c Canada United_States -cc USD -s 2004-01-01
```
![oil production macro](https://user-images.githubusercontent.com/46355364/158367787-4e7536c2-9d35-4bf6-9eba-cd1298d925e1.png)

```
2022 Mar 15, 07:11 (✨) /economy/ $ macro -sp
┏━━━━━━━━━━━┳━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓
┃ Parameter ┃ Description                           ┃
┡━━━━━━━━━━━╇━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┩
│ RGDP      │ Real gross domestic product           │
├───────────┼───────────────────────────────────────┤
│ RPRC      │ Real private consumption              │
├───────────┼───────────────────────────────────────┤
│ RPUC      │ Real public consumption               │
├───────────┼───────────────────────────────────────┤
│ RGFCF     │ Real gross fixed capital formation    │
├───────────┼───────────────────────────────────────┤
│ REXP      │ Real exports of goods and services    │
├───────────┼───────────────────────────────────────┤
│ RIMP      │ Real imports of goods and services    │
├───────────┼───────────────────────────────────────┤
│ GDP       │ Gross domestic product                │
├───────────┼───────────────────────────────────────┤
│ PRC       │ Private consumption                   │
├───────────┼───────────────────────────────────────┤
│ PUC       │ Public consumption                    │
├───────────┼───────────────────────────────────────┤
│ GFCF      │ Gross fixed capital formation         │
├───────────┼───────────────────────────────────────┤
│ EXP       │ Exports of goods and services         │
├───────────┼───────────────────────────────────────┤
│ IMP       │ Imports of goods and services         │
├───────────┼───────────────────────────────────────┤
│ CPI       │ Consumer price index                  │
├───────────┼───────────────────────────────────────┤
│ PPI       │ Producer price index                  │
├───────────┼───────────────────────────────────────┤
│ CORE      │ Core consumer price index             │
├───────────┼───────────────────────────────────────┤
│ URATE     │ Unemployment                          │
├───────────┼───────────────────────────────────────┤
│ EMP       │ Employment                            │
├───────────┼───────────────────────────────────────┤
│ ACOIO     │ Active population                     │
├───────────┼───────────────────────────────────────┤
│ EMRATIO   │ Employment to working age population  │
├───────────┼───────────────────────────────────────┤
│ RETA      │ Retail trade                          │
├───────────┼───────────────────────────────────────┤
│ CONF      │ Consumer confidence index             │
├───────────┼───────────────────────────────────────┤
│ IP        │ Industrial production                 │
├───────────┼───────────────────────────────────────┤
│ CP        │ Construction production               │
├───────────┼───────────────────────────────────────┤
│ GBAL      │ Government balance                    │
├───────────┼───────────────────────────────────────┤
│ GREV      │ General government total revenue      │
├───────────┼───────────────────────────────────────┤
│ GSPE      │ General government total expenditure  │
├───────────┼───────────────────────────────────────┤
│ GDEBT     │ Government debt                       │
├───────────┼───────────────────────────────────────┤
│ CA        │ Current account balance               │
├───────────┼───────────────────────────────────────┤
│ NIIP      │ Net international investment position │
├───────────┼───────────────────────────────────────┤
│ Y10YD     │ Long term yield (10-year)             │
├───────────┼───────────────────────────────────────┤
│ M3YD      │ 3 month yield                         │
├───────────┼───────────────────────────────────────┤
│ HOU       │ House price index                     │
├───────────┼───────────────────────────────────────┤
│ OILPROD   │ Oil production                        │
├───────────┼───────────────────────────────────────┤
│ POP       │ Population                            │
└───────────┴───────────────────────────────────────┘
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
