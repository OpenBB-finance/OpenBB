# Jupyter Ecosystem integration

The Jupyter ecosystem has created Open Source tools that have become the de-facto
standard for data related tasks.

This folder contains source code for a bunch of tools that help using the functionality
of the terminal in connection with Jupyter:

1. Jupyter Lab Extensions for using OpenBB Terminal

## 1. Jupyter Lab Extensions for using OpenBB Terminal

Documentation, OpenBB and GOpenBB-settings are 3 Jupyter Lab extensions that illustrate how
the terminal can be integrated with Jupyter Lab based IDEs.

_NOTE: The extensions should be considered prototypes and are not production-ready._

1. Only bash is supported (only macOS, Linux and WSL). No support for Windows powershell or command prompt.
2. The input values are not escaped

### Installation

To install the Terminal Launcher and the Settings Extensions run the following commands from the [root folder of the project](/):

```bash
pip install jupyterlab/openbb
pip install jupyterlab/openbb-settings
pip install jupyterlab/documentation
jupyter labextension install jupyterlab/openbb
jupyter labextension install jupyterlab/openbb-settings
jupyter labextension install jupyterlab/documentation
```

### Development setup

In this section `openbb` extension will be used as an example.

- In one terminal window `cd` into the launcher extension folder and build the extension:

```bash
cd openbb
jlpm
pip install -e .
jlpm run build
jupyter labextension develop . --overwrite
jlpm run watch
```

- In the second tab run jupyter lab

```bash
jupyter lab
```

---
