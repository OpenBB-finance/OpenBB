#!/bin/bash

# stty erase ^h
poetry run jupyter notebook --ip=0.0.0.0 &
poetry run python terminal.py
