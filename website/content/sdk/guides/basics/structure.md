---
title: Structure of the SDK
sidebar_position: 1
---

## Importing the SDK

Once you have the OpenBB SDK installed, the first step is to import the OpenBB SDK in your preferred code editor. Nearly everything required to interact with any function from the OpenBB Terminal gets imported in one line. Begin a Python script or Notebook file with:

```python
from openbb_terminal.sdk import openbb
```

Note that most snippets used in the guides will assume the code block above is used, and that the `Python kernel` selected is the environment created during the [installation process](/sdk/quickstart/installation).

## Navigation

In the same way how the OpenBB Terminal is operated, functions are divided into menus which can be navigated after code completion is activated. Entering a period, `.`, after `openbb`, will display the Sub-menus available.

![Navigation](https://user-images.githubusercontent.com/85772166/202795900-5f1cb00a-a0ff-4899-b6e2-c5af54b653d1.png "Navigation")

An alternate way to view the contents of a menu is to use Python's built-in help.

```python
help(openbb.stocks.dd)
```

### Docstrings

In addition to Python's built-in help, docstrings are also displayed in the Contextual Help window, within a Jupyter environment; type hints are included.

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