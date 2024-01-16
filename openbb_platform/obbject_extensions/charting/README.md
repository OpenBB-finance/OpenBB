# OpenBB Charting extension

This extension provides a charting library for OpenBB Platform.

The library includes:

- a charting infrastructure based on Plotly
- a set of charting components
- prebuilt charts for a set of commands that are built-in OpenBB extensions

## Installation

To install the extension, run the following command in this folder:

```bash
pip install openbb-charting
```

## PyWry dependency on Linux

The PyWry dependency handles the display of interactive charts and tables in a separate window. It is installed automatically with the OpenBB Charting extension.

When using Linux distributions, the PyWry dependency requires certain dependencies to be installed first.

- Debian-based / Ubuntu / Mint:
`sudo apt install libwebkit2gtk-4.0-dev`

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

> Note: The `show()` method currently works either in a Jupyter Notebook or in a standalone python script with a PyWry based backend properly initialized.

## Add a visualization to an existing Platform command

One should first ensure that the already implemented endpoint is available in the [charting router](/openbb_platform/extensions/charting/openbb_charting/charting_router.py).

To do so, you can run:
 `python openbb_platform/extensions/charting/openbb_charting/builder.py` - which will read all the available endpoints and add them to the charting router.

Afterwards, you'll need to add the visualization to the [charting router](/openbb_platform/extensions/charting/openbb_charting/charting_router.py). The convention to match the endpoint with the respective charting function is the following:

- `/equity/price/historical` -> `equity_price_historical`
- `/technical/ema` -> `technical_ema`

When you spot the charting function on the charting router file, you can add the visualization to it.

The implementation should leverage the already existing classes and methods to do so, namely:

- `OpenBBFigure`
- `OpenBBFigureTable`
- `PlotlyTA`

Note that the return of each charting function should respect the already defined return types: `Tuple[OpenBBFigure, Dict[str, Any]]`.

The returned tuple contains a `OpenBBFigure` that is an interactive plotly figure which can be used in a Python interpreter, and a `Dict[str, Any]` that contains the raw data leveraged by the API.

After you're done implementing the charting function, you can use either the Python interface or the API to get the chart. To do so, you'll only need to set the already available `chart` argument to `True`.

### Using the `to_chart` OBBject method

The `OBBject` is the custom OpenBB object that is returned by the Platform commands.
It implements a set of `to_<something>` functions that enable the user to easily transform the data into a different format.

The `to_chart` function should be taken as an advanced feature, as it requires the user to have a good understanding of the charting extension and the `OpenBBFigure` class.

The user can use any number of `**kwargs` that will be passed to the `PlotlyTA` class in order to build custom visualizations with custom indicators and similar.

Refer to the [`to_chart` implementation](openbb_charting/core/to_chart.py) for further details.

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
    res.to_chart(**{"indicators": indicators})

  ```

- Get all the available indicators

    ```python

    from openbb_charting.core.plotly_ta.data_classes import ChartIndicators
    ChartIndicators.get_available_indicators()

    ```
