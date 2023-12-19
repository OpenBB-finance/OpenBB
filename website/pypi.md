# OpenBB SDK v3

[![Downloads](https://static.pepy.tech/badge/openbb)](https://pepy.tech/project/openbb)
[![LatestRelease](https://badge.fury.io/py/openbb.svg)](https://github.com/OpenBB-finance/OpenBBTerminal)

| OpenBB is committed to build the future of investment research by focusing on an open source infrastructure accessible to everyone, everywhere. |
|:--:|
| ![OpenBBLogo](https://user-images.githubusercontent.com/25267873/218899768-1f0964b8-326c-4f35-af6f-ea0946ac970b.png) |
| Check our website at [openbb.co](www.openbb.co) |

## Overview

OpenBB SDK provides a convenient way to access raw financial data from multiple data providers. This allows users to build custom financial dashboards and reports in minutes.

More information on this product can be found [here](https://openbb.co/products/sdk)

## Installation

The command below provides access to the core functionalities behind the [OpenBB Terminal](https://openbb.co/products/terminal).

```python
pip install openbb==3.2.4
```

If you wish to utilize our **Portfolio Optimization** or **Machine Learning / Artificial Intelligence** toolkits, please see instructions [here](https://docs.openbb.co/terminal/installation).

## Usage

Access our fully fledged financial SDK with a single line of python code.

```python
from openbb_terminal.sdk import openbb
```

Everything you need to use the OpenBB SDK can be found on our [Official Documentation](https://docs.openbb.co/sdk).

Main uses cases can be seen below.
___

### RAW FINANCIAL DATA AT YOUR FINGERTIPS

Access raw financial data from any data source that you are interested. The open source nature of this SDK makes it so that this is an ever-growing project and that everyone can contribute to.

![Stocks Load](https://user-images.githubusercontent.com/25267873/218906336-cebd1fc8-7e7a-45bc-a5fc-641eb19c3e8c.png)

### GENERATE INSIGHTS 10X FASTER

For most of the functionalities, adding `_chart` to the function will allow you to visualize the output directly from a Jupyter Notebook. Not only speeding up the time it takes to create a plot for the data you are interested in, but making building custom reports much faster.

![Economy Treasury Chart](https://user-images.githubusercontent.com/25267873/218906112-b2272d43-11fc-4ec1-9a8f-b2d8e2ed7dc1.png)
