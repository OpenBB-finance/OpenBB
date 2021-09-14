#!/bin/bash

source $(poetry env info --path)/bin/activate
#export PS1="(gst) > "
# stty erase ^h
jupyter lab --ip=0.0.0.0
#poetry run python terminal.py
