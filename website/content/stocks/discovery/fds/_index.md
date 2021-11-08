```
usage: fds [-c --country COUNTRY [COUNTRY ...]] [-s --sector SECTOR [SECTOR ...]]
        [-i --industry INDUSTRY [INDUSTRY ...]] [-n --name NAME [NAME ...]]
        [-d --description DESCRIPTION [DESCRIPTION ...]] [-ie --include_exchanges] [-a --amount AMOUNT]
        [-o --options {countries,sectors,industries}] [-h]
```
Display a selection of Equities based on country, sector, industry, name and/or description filtered by market cap.
If no arguments are given, return the equities with the highest market cap.

Source: https://github.com/JerBouma/FinanceDatabase

* -c --country: Specify the Equities selection based on a country
* -s --sector: Specify the Equities selection based on a sector
* -i --industry: Specify the Equities selection based on an industry
* -n --name: Specify the Equities selection based on the name
* -d --description: Specify the Equities selection based on the description (not shown in table)
* -ie --include_exchanges: If used, you also obtain Equities from different exchanges (a lot of data) 
* -a --amount: Enter the number of Equities you wish to see in the Tabulate window
* -o --options: Obtain the available options for country, sector and industry
<img width="1400" alt="Feature Screeshot - fds" src="https://user-images.githubusercontent.com/85772166/140450303-ab41459b-2c8c-4115-9a44-226c120e8e67.png">
