---
title: Introduction to Economy
keywords: "fred, sdk, api, bonds, treasury, treasuries, spread, events, calendar, futures, future, yield, curve, macro, index, indices, performance, bigmac, series, gdp, indicators"
excerpt: "This guide introduces the Economy module within the OpenBB SDK and provides some use examples."
geekdocCollapseSection: true
---
The Economy module wraps the functions of the <a href="https://openbb-finance.github.io/OpenBBTerminal/terminal/economy/" target="_blank">Economy menu</a>, within the <a href="https://openbb-finance.github.io/OpenBBTerminal/terminal/" target="_blank">OpenBB Terminal</a>, and provides the user with more control over their workflow. In a Jupyter Notebook environment, it is quick and easy to get going. Start a new `.ipynb` Notebook file, or a `.py` Python script by importing the necessary modules for the tasks at hand. For the purpose of these examples, two additional modules will be imported:
````
from openbb_terminal.sdk import openbb
import pandas as pd
%matplotlib inline
````
Jupyter Lab can be launched from the command line, in the `OpenBBTerminal` folder and with the Conda environment already activated, by entering either: `jupyter lab`, or, `jupyter notebook`; and then pressing `enter`. This will launch a browser window for the session.

To get the most out of these functions, it is highly recommended to acquire an API key to access the FRED data library. This is free, just create an account <a href="https://fred.stlouisfed.org" target="_blank"> here</a>, then look in the account settings for the assigned API key.

Refer to the <a href="https://openbb-finance.github.io/OpenBBTerminal/SDK/keys/" target="_blank">Introduction Guide to API Keys within the OpenBB SDK</a> for instructions on setting the API keys, with the Keys module.

## How to Use

With the modules imported, the code completion is activated after entering the `.` after, `openbb.economy`

![Economy Menu Code Completion](https://user-images.githubusercontent.com/85772166/198433265-69073c7a-5494-4275-a0e7-bdcc1c4b431c.png)

Just like the other modules, there are several methods for returning the docstrings of a single function:

  -  Use Python's built-in help: `help(openbb.economy.index)`
  -  View the documentation online: https://openbb-finance.github.io/OpenBBTerminal/SDK/economy/index/
  -  Open the Contextual Help window
````
openbb.economy.index(indices = ['nyse', 'nasdaq', 'amex', 'ca_tsx', 'dow_dji', 'in_nse50'])
````

![Contextual Help](https://user-images.githubusercontent.com/85772166/198433406-b61f3bed-21fe-47c3-95d0-ee3c17931f92.png)

There are some differences when comparing SDK functions against the OpenBB Terminal commands. For example, the Terminal command, `/economy/index --show`, becomes: `openbb.economy.available_indices()`. This returns a list of dictionaries; convert them to a DataFrame with:
````
pd.DataFrame.from_dict(openbb.economy.available_indices()).transpose()
````

![openbb.economy.available_indices()](https://user-images.githubusercontent.com/85772166/198433551-921ec05d-6a96-44ff-b164-c7af18602d82.png)

To display a chart inside the Notebook, instead of a DataFrame, add `chart = True` to the command syntax. For example:
````
openbb.economy.index(indices = ['sp500', 'sp500tr'], chart = True)
````

![S&P 500 vs. S&P 500 Total Return Index](https://user-images.githubusercontent.com/85772166/198433750-c62794ee-a26e-4da8-85b7-0782196efd11.png)

It is also possible to make a DataFrame of a stock and an index. The list of symbols fed to the `index` function can be the dictionary name from, `openbb.economy.available_indices()`, or it can be a ticker symbol that is recognized by `yFinance`. As an example:
````
openbb.economy.index(indices = ['move', 'aapl'], chart = True, start_date = '2016-01-01')
````

![AAPL vs MOVE Index](https://user-images.githubusercontent.com/85772166/198433917-ebd06b62-e5a1-4d53-94be-ea2680297139.png)

Another notable difference, between OpenBB Terminal commands and their corresponding SDK functions, is the way `fred` works. With the OpenBB SDK, the `fred` function is broken down into four components, as shown here:

![FRED functions in the OpenBB SDK](https://user-images.githubusercontent.com/85772166/198434069-a0f4deb0-6db3-421e-bd49-2a3e63565949.png)

`openbb.economy.fred_yield_curve()` returns a Tuple with the raw data for composing the chart presented by the OpenBB Terminal function, `/economy/ycrv --source fred`.

````
data, date = openbb.economy.fred_yield_curve()
````

![FRED Yield Curve Raw Data](https://user-images.githubusercontent.com/85772166/198434188-0eacedab-ff27-40dc-917d-c7bf5929d9ad.png)

The FRED library can be searched, by key words and phrases, in two ways:

  -  `openbb.economy.fred_notes('search term')`
  -  `openbb.economy.fred_ids('search term')`

The former, giving more details than the latter.

![FRED Query](https://user-images.githubusercontent.com/85772166/198434480-97d630fb-62a1-45b7-b8d2-a171fdf3c0ae.png)

Retrieving the time-series data is then accomplished by using the `fred_series` function:

````
openbb.economy.fred_series(series_ids = ['PCENOW','GDPNOW'])
````

![fred_series](https://user-images.githubusercontent.com/85772166/198434607-8e421db7-56fa-4dda-8796-12a28373c1d8.png)

Other functions more closely resemble their counterpart within the OpenBB Terminal, such as: `openbb.economy.bigmac(country_codes = ['CAN','USA'])`

![BigMac Index](https://user-images.githubusercontent.com/85772166/198434807-59b77a92-bbaa-4916-9b03-2e375bfcbc79.png)

Adding `chart = True` to the syntax will display the graph:

````
openbb.economy.bigmac(country_codes = ['CAN','USA'], chart = True)
````

![BigMac Index Chart](https://user-images.githubusercontent.com/85772166/198435081-63077337-ff31-49f2-b2df-f46c9571e98d.png)

The `performance` and `valuation` functions, compared against the OpenBB Terminal, are also similar. Note that data returned by these functions are inclusive only of companies with an active and public US listing.

````
openbb.economy.performance()
openbb.economy.valuation()
````

![Economic Performance](https://user-images.githubusercontent.com/85772166/198435213-4c9158f1-3432-442a-b2bb-edf282264e4a.png)

````
openbb.economy.performance(group = 'industry')
````

![Performance by Industry](https://user-images.githubusercontent.com/85772166/198435374-0bb6a0fc-9fb0-4de4-bab0-c7b959694193.png)
