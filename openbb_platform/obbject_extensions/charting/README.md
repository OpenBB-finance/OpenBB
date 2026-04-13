# OpenBB Charting extension

This extension provides a charting library for OpenBB Platform.

The library includes:

- a charting infrastructure based on Plotly
- a set of charting components
- prebuilt charts for a set of commands that are built-in OpenBB extensions

>[!NOTE]
> The charting library is an `OBBject` extension which means you'll have the functionality it exposes on every command result.

## Installation

To install the extension, run the following command in this folder:

```bash
pip install openbb-charting
```

To enable display in a native OS window, install the PyWry extra.

```bash
pip install "openbb-charting[pywry]"
```

### PyWry dependency on Linux

When using Linux distributions, the PyWry dependency requires certain dependencies to be installed first.

- Debian-based / Ubuntu / Mint:
`sudo apt install libwebkit2gtk-4.1-dev libgtk-3-dev`

- Arch Linux / Manjaro:
`sudo pacman -S webkit2gtk`

- Fedora:
`sudo dnf install gtk3-devel webkit2gtk3-devel`

## Usage

To use the extension, run any of the OpenBB Platform endpoints with the `chart` argument set to `True`.

Here's an example of how it would look like in a python interface:

```python
from openbb import obb
equity_data = obb.equity.price.historical(symbol="TSLA", chart=True)
```

This results in a `OBBject` object containing a `chart` attribute, which contains Plotly JSON data.

In order to display the chart, you need to call the `show()` method:

```python
equity_data.show()
```

Alternatively, `openbb-charting` is an `OBBject` accessor and its methods can be used directly from any instance.

```python
from openbb import obb
res = obb.equity.price.historical("AAPL")
res.charting.show()
```

The above code will produce the same effect as the previous example.

## Custom Charts and Data

Various types of charts can be generated from Pandas DataFrames without needing to understand the Plotly library.

The methods are exposed as part of the `OBBject` accessor class. The `data` parameter can be passed as a list object from `OBBject.results`, or any Pandas DataFrame instance.

```python
res = obb.equity.price.historical("AAPL", chart=True)

surface_3d = res.charting.create_3d_surface
bar_chart = res.charting.create_bar_chart
line_chart = res.charting.create_line_chart
correlation_matrix = res.charting.create_correlation_matrix
```

### Discovering available charts

Not all the endpoints have dedicated charts. To discover which endpoints are supported, you can run the following command:

```python
from openbb_charting import Charting
Charting.functions()
```

### Using the `to_chart` method

The `to_chart` function should be taken as an advanced feature, as it requires the user to have a good understanding of the charting extension and the `OpenBBFigure` class.

The user can use any number of `**kwargs` that will be passed to the `PlotlyTA` class in order to build custom visualizations with custom indicators and similar.

> Note that, this method will only work to some limited extent with data that is not standardized.
> Also, it is currently designed only to handle time series (OHLCV) data.

Example usage:

- Plotting a time series with TA indicators

  ```python

    from openbb import obb
    res = obb.equity.price.historical("AAPL")

    indicators = dict(
        sma=dict(length=[20,30,50]),
        adx=dict(length=14),
        rsi=dict(length=14),
        macd=dict(fast=12, slow=26, signal=9),
        bbands=dict(length=20, std=2),
        stoch=dict(length=14),
        ema=dict(length=[20,30,50]),
    )
    res.charting.to_chart(**{"indicators": indicators})

  ```

- Get all the available indicators

    ```python

    # if you have a command result already
    res.charting.indicators

    # or if you want to know in standalone fashion
    from openbb_charting import Charting
    Charting.indicators()

    ```

## Add a visualization to an existing Platform command

To add a visualization to an existing command, you'll need to add a `poetry` plugin to your `pyproject.toml` file. The syntax should be the following:

```toml
[tool.poetry.plugins."openbb_charting_extension"]
my_extension = "openbb_my_extension.my_extension_views:MyExtensionViews"
```

Where the `openbb_charting_extension` is **mandatory**, otherwise the charting extension won't be able to find the visualization.

And the suggested structure for the `my_extension_views` module is the following:

```python
"""Views for MyExtension."""

from typing import Any, Dict, Tuple

from openbb_charting.charts.price_historical import price_historical
from openbb_charting.core.openbb_figure import OpenBBFigure


class MyExtensionViews:
    """MyExtension Views."""

    @staticmethod
    def my_extension_price_historical(
        **kwargs,
    ) -> Tuple[OpenBBFigure, Dict[str, Any]]:
        """MyExtension Price Historical Chart."""
        return price_historical(**kwargs)
```

> Note that `my_extension_views` lives under the `openbb_my_extension` package.

Afterwards, you'll need to add the visualization to your new `MyExtensionViews` class. The convention to match the endpoint with the respective charting function is the following:

- `/equity/price/historical` -> `equity_price_historical`
- `/technical/ema` -> `technical_ema`
- `/my_extension/price_historical` -> `my_extension_price_historical`

When you spot the charting function on the charting router file, you can add the visualization to it.

The implementation should leverage the already existing classes and methods to do so, namely:

- `OpenBBFigure`
- `PlotlyTA`

Note that the return of each charting function should respect the already defined return types: `Tuple[OpenBBFigure, Dict[str, Any]]`.

The returned tuple contains a `OpenBBFigure` that is an interactive Plotly figure which can be used in a Python interpreter, and a `Dict[str, Any]` that contains the raw data leveraged by the API.

After you're done implementing the charting function, you can use either the Python interface or the API to get the chart. To do so, you'll only need to set the already available `chart` argument to `True`.
Or accessing the `charting` attribute of any returned `OBBject` object: `my_obbject.charting.show()`.
