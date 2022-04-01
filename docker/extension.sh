#!/bin/bash

source $(poetry env info --path)/bin/activate

pip install -e jupyterlab/openbb
pip install -e jupyterlab/openbbterminal-settings
pip install -e jupyterlab/documentation
jupyter-labextension install jupyterlab/openbb
jupyter-labextension install jupyterlab/openbb-settings
jupyter-labextension install jupyterlab/documentation
