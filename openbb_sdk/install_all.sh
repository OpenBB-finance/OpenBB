#!/bin/bash

# Finds the current python executable
PYTHON_EXEC=$(which python)

# Install all openbb sdk (core+provider), extensions and providers in editable mode
find extensions providers sdk -type f -name "pyproject.toml" -execdir sh -c '
    echo "Installing $(basename "$PWD")..."
    "$1" -m pip install -U -e "${PWD}" >/dev/null 2>&1
    if [ $? -ne 0 ]; then
        echo "Script terminated!"
        exit 1
    fi
' _ "$PYTHON_EXEC" {} +
