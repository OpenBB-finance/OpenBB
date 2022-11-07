---
title: Introduction to Quantitative Analysis
keywords: "qa, quant, quantitative, bw, var, es, kurtosis, normality, omega, quantile, rolling, sharpe, skew, spread, summary, unitroot, var, math"
excerpt: "This guide introduces the Quantitative Analysis module, and provides some examples."
geekdocCollapseSection: true
---
The `qa` module replicates the features of the Quantitative Analysis menu, within the <a href="https://openbb-finance.github.io/OpenBBTerminal/terminal/common/qa/" target="_blank">OpenBB Terminal</a>, for the SDK environment. It provides users with more ways to interact with the library of functions, and provides cross-disciplinary utility. To activate the code completion for the menu, enter `.` after, `openbb.common.qa`.

![The QA Module](https://user-images.githubusercontent.com/85772166/200109595-dbfde965-72b4-40fc-88bf-95f34a30f5d9.png "The QA Module")

## How to Use

With the modules imported, the next step would be to collect data for analysis. In this example, the Quandl API will be used. To pass the key to the URL string, import:

```python

import openbb_terminal.config_terminal as cfg

```
The credentials can then be passed with:

```python
f"{cfg.API_KEY_QUANDL}"
```

As a functional code block, this looks like:

```python

from openbb_terminal.sdk import openbb
import openbb_terminal.config_terminal as cfg
import pandas as pd
import matplotlib.pyplot as plt

%matplotlib widget
```

```python
payload = pd.read_json('https://data.nasdaq.com/api/v3/datasets/MULTPL/SHILLER_PE_RATIO_MONTH.json?api_key='f"{cfg.API_KEY_QUANDL}")
payload = pd.DataFrame(payload).transpose()
shiller_pe = payload.data.dataset
```

![Loading Data](https://user-images.githubusercontent.com/85772166/200109605-4cdd01b2-2974-4222-bb6c-0bf14c593cb5.png "Loading Data")

Now, with the data loaded, the next block will utilize the `skew` function, to target the monthly Shiller P/E Ratio of the S&P 500 from inception.

```python
shiller_df = pd.DataFrame(columns = ['Date', 'Shiller P/E Ratio', 'Skew'])
shiller_pe = pd.DataFrame(shiller_pe)
shiller_skew = openbb.common.qa.skew(data = shiller_pe[1], window = 3)

shiller_df['Date'] = shiller_pe[0].values
shiller_df['Shiller P/E Ratio'] = shiller_pe[1].values
shiller_df['Skew'] = shiller_skew
shiller_df.set_index(keys = ['Date'], inplace = True)

shiller_df.tail()
```

![Skew of Monthly S&P 500 Shiller P/E Ratio](https://user-images.githubusercontent.com/85772166/200109627-0e532041-dd6a-41ef-ad17-41acd1b58caf.png "Skew of Monthly S&P 500 Shiller P/E Ratio")

Get a summary of the DataFrame:

```python
openbb.common.qa.summary(shiller_df)
```

![openbb.common.qa.summary](https://user-images.githubusercontent.com/85772166/200109649-fdf9b1f8-6e7e-47df-8baa-b1e265872b12.png "openbb.common.qa.summary")

Insert the rolling mean and standard deviation of a target column with, `openbb.common.qa.rolling`:

```python
mean,std = openbb.common.qa.rolling(shiller_df['Shiller P/E Ratio'])
mean.rename(columns = {'Shiller P/E Ratio': 'Mean'}, inplace = True)
std.rename(columns = {'Shiller P/E Ratio': 'Std'}, inplace = True)
rolling = mean.join(std)
shiller_df = shiller_df.join(rolling)

shiller_df
```

![openbb.common.qa.rolling](https://user-images.githubusercontent.com/85772166/200109671-ec0d62ac-fedc-4690-a972-b326a1f05da3.png "openbb.common.qa.rolling")

Calculate and join the Sharpe Ratio of, for example, the rolling mean average of the Shiller P/E ratio:

```python
sharpe = pd.DataFrame(openbb.common.qa.sharpe(data = shiller_df['Mean'], window = 12, rfr = 3))
sharpe.rename(columns = {'Mean': 'Sharpe'}, inplace = True)
shiller_df = shiller_df.join(sharpe)
```

![openbb.common.qa.sharpe](https://user-images.githubusercontent.com/85772166/200109727-85736e12-85c2-43d6-97e0-4a95cf40bd6f.png "openbb.common.qa.sharpe")
