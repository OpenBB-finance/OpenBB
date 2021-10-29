```
usage: fds [-c --category CATEGORY [CATEGORY ...]] [-n --name NAME [NAME ...]]
        [-d --description DESCRIPTION [DESCRIPTION ...]] [-ie --include_exchanges]
        [-a --amount AMOUNT] [-o --options] [-h]
```
Display a selection of ETFs based on category, name and/or description filtered by total assets. Returns the top ETFs
when no argument is given.

* -c --category: Specify the ETF selection based on a category
* -n --name: Specify the ETF selection based on the name
* -d --description: Specify the ETF selection based on the description (not shown in table)
* -ie --include_exchanges: If used, you also obtain ETFs from different exchanges (a lot of data) 
* -a --amount: Enter the number of ETFs you wish to see in the Tabulate window
* -o --options: Obtain the available categories
