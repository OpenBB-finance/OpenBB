---
title: macro
description: Learn how to retrieve and manipulate a variety of macro data from numerous
  countries using various parameters and transformations. The page provides examples
  and details of the functionalities.
keywords:
- macro data
- Gross Domestic Product
- Treasury Yields
- Employment figures
- Government components
- Consumer and Producer Indices
- EconDB
- macro parameters
- data transformation
- macro programming
- currency conversion
---

import HeadTitle from '@site/src/components/General/HeadTitle.tsx';

<HeadTitle title="economy /macro - Reference | OpenBB Terminal Docs" />

Get a broad selection of macro data from one or multiple countries. This includes Gross Domestic Product (RGDP & GDP) and the underlying components, Treasury Yields (Y10YD & M3YD), Employment figures (URATE, EMP, AC0I0 and EMRATIO), Government components (e.g. GBAL & GREV), Consumer and Producer Indices (CPI & PPI) and a variety of other indicators. [Source: EconDB]

### Usage

```python wordwrap
macro [-p PARAMETERS] [-c COUNTRIES] [-t {,TPOP,TOYA,TUSD,TPGP,TNOR}] [--show {parameters,countries,transform}] [-s START_DATE] [-e END_DATE] [--convert {ALL,ARS,AUD,EUR,AZN,BDT,BYR,EUR,BTN,BAM,BWP,BRL,BGN,KHR,XAF,CAD,CLP,CNY,COP,HRK,EUR,CZK,DKK,DOP,EGP,EUR,EUR,EUR,EUR,EUR,EUR,HNL,HKD,HUF,INR,IDR,IRR,EUR,ILS,EUR,JPY,KZT,LAK,EUR,LBP,EUR,EUR,MKD,MYR,EUR,MXN,MNT,EUR,NZD,NGN,NOK,OMR,PKR,PAB,PYG,PEN,PHP,PLN,EUR,QAR,RON,RUB,SAR,RSD,SGD,EUR,EUR,ZAR,KRW,EUR,SEK,CHF,TWD,THB,TND,TRY,UAH,AED,GBP,USD,UZS,VEF,VND}]
```

---

## Parameters

| Name | Parameter | Description | Default | Optional | Choices |
| ---- | --------- | ----------- | ------- | -------- | ------- |
| parameters | -p  --parameters | Abbreviation(s) of the Macro Economic data | CPI | True | None |
| countries | -c  --countries | The country or countries you wish to show data for | united_states | True | None |
| transform | -t  --transform | The transformation to apply to the data |  | True | , TPOP, TOYA, TUSD, TPGP, TNOR |
| show | --show | Show parameters and what they represent using 'parameters' or countries and their currencies using 'countries' | None | True | parameters, countries, transform |
| start_date | -s  --start | The start date of the data (format: YEAR-MONTH-DAY, i.e. 2010-12-31) | None | True | None |
| end_date | -e  --end | The end date of the data (format: YEAR-MONTH-DAY, i.e. 2021-06-20) | None | True | None |
| currency | --convert | Convert the currency of the chosen country to a specified currency. To find the currency symbols use '--show countries' | False | True | dict_values(['ALL', 'ARS', 'AUD', 'EUR', 'AZN', 'BDT', 'BYR', 'EUR', 'BTN', 'BAM', 'BWP', 'BRL', 'BGN', 'KHR', 'XAF', 'CAD', 'CLP', 'CNY', 'COP', 'HRK', 'EUR', 'CZK', 'DKK', 'DOP', 'EGP', 'EUR', 'EUR', 'EUR', 'EUR', 'EUR', 'EUR', 'HNL', 'HKD', 'HUF', 'INR', 'IDR', 'IRR', 'EUR', 'ILS', 'EUR', 'JPY', 'KZT', 'LAK', 'EUR', 'LBP', 'EUR', 'EUR', 'MKD', 'MYR', 'EUR', 'MXN', 'MNT', 'EUR', 'NZD', 'NGN', 'NOK', 'OMR', 'PKR', 'PAB', 'PYG', 'PEN', 'PHP', 'PLN', 'EUR', 'QAR', 'RON', 'RUB', 'SAR', 'RSD', 'SGD', 'EUR', 'EUR', 'ZAR', 'KRW', 'EUR', 'SEK', 'CHF', 'TWD', 'THB', 'TND', 'TRY', 'UAH', 'AED', 'GBP', 'USD', 'UZS', 'VEF', 'VND']) |


---

## Examples

```python
2022 Mar 15, 07:20 (🦋) /economy/ $ macro -p CONF -c netherlands,germany,france -s 2005-01-01 -e 2022-01-01
```
![macro conf netherlands germany france](https://user-images.githubusercontent.com/46355364/159249787-a030cd2c-0b29-4522-a1a9-db0245d55d9f.png)

![oil production macro](https://user-images.githubusercontent.com/46355364/159251277-9381cc0a-7efe-41ce-af93-41d832103a1e.png)

![argentina gross domestic product in dollars](https://user-images.githubusercontent.com/46355364/159253210-c7135b12-b04a-49e4-8896-d03e4c25f520.png)

---
