```
usage: fds [--country --c COUNTRY [COUNTRY ...]] [--sector --s SECTOR [SECTOR ...]]
        [--industry --i INDUSTRY [INDUSTRY ...]] [--name --n NAME [NAME ...]]
        [--description --d DESCRIPTION [DESCRIPTION ...]] [--amount --a AMOUNT]
        [--options --o {countries,sectors,industries}] [-h]
```
Display a selection of Equities based on country, sector, industry, name and/or description filtered by market cap.
If no arguments are given, return the equities with the highest market cap.

* --country --c: Specify the Equities selection based on a country
* --sector --s: Specify the Equities selection based on a sector
* --industry --i: Specify the Equities selection based on an industry
* --name --n: Specify the Equities selection based on the name
* --description --d: Specify the Equities selection based on the description (not shown in table)
* --amount --a Enter the number of Equities you wish to see in the Tabulate window
* --options --o: Obtain the available options for country, sector and industry
