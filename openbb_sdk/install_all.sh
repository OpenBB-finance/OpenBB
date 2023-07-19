#!/bin/bash

# Finds the current python executable
PYTHON_EXEC=$(which python)

# Install all openbb extensions and providers
find extensions providers -type f -name "pyproject.toml" -execdir sh -c '
    echo "Installing $(basename "$PWD")..."
    "$1" -m pip install -U -e "${PWD}"
    if [ $? -ne 0 ]; then
        echo "Script terminated!"
        exit 1
    fi
' _ "$PYTHON_EXEC" {} +
