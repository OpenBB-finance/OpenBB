# OpenBB Charting extension

This extension provides a charting library for OpenBB SDK.

The library includes:

- charting infrastructure based on Plotly and
- a set of charting components
- prebuilt charts for a set of commands that are available in built-in OpenBB SDK extensions

## Installation

To install the extension, run the following command in this folder:

```bash
pip install .
```

## PyWry dependency on Linux

The PyWry dependency handles display of interactive charts and tables in a separate window. It is installed automatically with the OpenBB Charting extension.

When using linux distributions, the PyWry dependency requires certain dependencies to be installed first.

Debian-based / Ubuntu / Mint:
`sudo apt install libwebkit2gtk-4.0-dev`

Arch Linux / Manjaro:
`sudo pacman -S webkit2gtk`

Fedora:
`sudo dnf install gtk3-devel webkit2gtk3-devel`
