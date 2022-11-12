---
title: API Keys
keywords: "api,keys,key,secret,token,bearer,credentials,secrets,data,sources"
excerpt: "This guide explains how to manage API keys within an OpenBB SDK environment."
geekdocCollapseSection: true
---
The `keys` module provides the same functionality as the <a href="https://openbb-finance.github.io/OpenBBTerminal/#accessing-other-sources-of-data-via-api-keys" target="_blank"> Keys menu</a> does in the <a href="https://openbb-finance.github.io/OpenBBTerminal/terminal/" target="_blank">OpenBB Terminal</a>. Each data source requiring authentication will have slight differences of required inputs. Refer to the table <a href="https://openbb-finance.github.io/OpenBBTerminal/#accessing-other-sources-of-data-via-api-keys" target="_blank">here</a> for a compiled list of links for each data source.

![openbb.keys.mykeys()](https://user-images.githubusercontent.com/85772166/198151758-7fdf1e00-29c2-4fb1-bfb1-7421cc9b8986.png)

## How to Use

Use Python's built-in `help` to print docstrings by entering, `help(openbb.keys.reddit)`. Alternatively, the contextual help window of a Jupyter session can be opened to view them.

![Contextual Help](https://user-images.githubusercontent.com/85772166/198360190-753d4fd8-768a-4de6-9c24-44491804914f.png)

Note that if `persist = False`, the credentials will not be retained in the local installation. Set as `persist = True` to apply them permanently to the local installation of the Terminal application, or SDK.

Expected values for all sources is printed with, `openbb.keys.get_keys_info()`, which describes what fields need to be included for each API.

![get_keys_info](https://user-images.githubusercontent.com/85772166/198151924-08f97592-08ce-4631-b333-0f6568124874.png)

Referencing the information above, they are then defined like, `openbb.keys.av(key='putyourkeyhere')`

A source with multiple inputs should be defined like, `openbb.keys.binance(key='apikeyhere', secret='thesecretstring')`

Code completion is activated after the `.` is added to `openbb.keys`. This provides a list which is browsable with the arrow keys.

![Code Completion](https://user-images.githubusercontent.com/85772166/198151847-a09e9589-43b8-4c40-9cd1-be18092a8004.png)

Enter multiple keys by creating a list of dictionaries:

![Multiple Keys](https://user-images.githubusercontent.com/85772166/198152166-94ed3544-a03a-4790-9b4a-c76f2419e3d5.png)

A simple CSV backup of all credentials can be generated from a Pandas DataFrame:

````
from openbb_terminal.sdk import openbb
import pandas as pd

keys_backup = openbb.keys.mykeys(show = True)
pd.DataFrame(keys_backup).to_csv('keys_backup.csv')
````
