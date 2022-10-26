---
title: API Keys
keywords: "api,keys,key,secret,token,bearer,credentials,secrets,data,sources"
excerpt: "This guide explains how to manage API keys within an OpenBB SDK environment."
geekdocCollapseSection: true
---
The `keys` module provides the same functionality as the <a href="https://openbb-finance.github.io/OpenBBTerminal/#accessing-other-sources-of-data-via-api-keys" target="_blank"> Keys menu</a> does in the <a href="https://openbb-finance.github.io/OpenBBTerminal/terminal/" target="_blank">OpenBB Terminal application</a>. Each data source requiring authentification will have slight differences of required inputs. Refer to the table <a href="https://openbb-finance.github.io/OpenBBTerminal/#accessing-other-sources-of-data-via-api-keys" target="_blank">here</a> for a compiled list of links for each data source.

![openbb.keys.mykeys()](https://user-images.githubusercontent.com/85772166/198151758-7fdf1e00-29c2-4fb1-bfb1-7421cc9b8986.png)

## How to Use

### Expected values for all sources is printed with:
````
openbb.keys.get_keys_info()
````

![get_keys_info](https://user-images.githubusercontent.com/85772166/198151924-08f97592-08ce-4631-b333-0f6568124874.png)

### Code completion is activated after the `.` is added to `openbb.keys`:

![Code Completion](https://user-images.githubusercontent.com/85772166/198151847-a09e9589-43b8-4c40-9cd1-be18092a8004.png)

### Use Python's built-in `help` to print docstrings:

````
help(openbb.keys.reddit)

Help on method set_reddit_key in module openbb_terminal.keys_model:

set_reddit_key(client_id: str, client_secret: str, password: str, username: str, useragent: str, persist: bool = False, show_output: bool = False) -> str method of openbb_terminal.sdk.FunctionFactory instance
    Set Reddit key
    Parameters
    ----------
        client_id: str
        client_secret: str
        password: str
        username: str
        useragent: str
        persist: bool
            If False, api key change will be contained to where it was changed. For example, Jupyter notebook.
            If True, api key change will be global, i.e. it will affect terminal environment variables.
            By default, False.
        show_output: bool
            Display status string or not. By default, False.
    Returns
    -------
    status: str
````

  -  Note that if `persist = False`, the credentials will not be retained in the local installation. Set as `persist = True` to apply them permanently to the local installation of the Terminal application, or SDK.

### Enter multiple keys by creating a list of dictionaries:

![Multiple Keys](https://user-images.githubusercontent.com/85772166/198152166-94ed3544-a03a-4790-9b4a-c76f2419e3d5.png)

### A simple CSV backup of all credentials can be made with:
````
from openbb_terminal.sdk import openbb
import pandas as pd

keys_backup = openbb.keys.mykeys(show = True)
pd.DataFrame(keys_backup).to_csv('keys_backup.csv')
````
