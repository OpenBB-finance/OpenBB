# OpenBB Charting extension

This extension provides a charting library for OpenBB SDK.

The library includes:

- a charting infrastructure based on Plotly
- a set of charting components
- prebuilt charts for a set of commands that are built-in OpenBB SDK extensions

## Installation

To install the extension, run the following command in this folder:

```bash
pip install openbb-charting
```

## PyWry dependency on Linux

The PyWry dependency handles display of interactive charts and tables in a separate window. It is installed automatically with the OpenBB Charting extension.

When using Linux distributions, the PyWry dependency requires certain dependencies to be installed first.

- Debian-based / Ubuntu / Mint:
`sudo apt install libwebkit2gtk-4.0-dev`

- Arch Linux / Manjaro:
`sudo pacman -S webkit2gtk`

- Fedora:
`sudo dnf install gtk3-devel webkit2gtk3-devel`


## Usage

To use the extension, run any of the OpenBB SDK endpoints with the `chart` argument set to `True`.

Here's an example how it would look like in a python interface:

```python
from openbb import obb
stock_data = obb.stocks.load(symbol="TSLA", chart=True)
```

This results in a `OBBject` object containing a `chart` attribute, which contains Plotly JSON data.

In order to display the chart, you need to call the `show()` method:

```python
stock_data.show()
```

> Note: The `show()` method currently works either in a Jupyter Notebook or in a standalone python script with a PyWry based backend properly initialized.
