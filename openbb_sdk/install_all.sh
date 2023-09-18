#!/bin/bash

# Finds the current python executable
PYTHON_EXEC=$(which python)

# Install all openbb sdk (core+provider), extensions and providers in editable mode
find openbb_sdk/extensions openbb_sdk/providers openbb_sdk/sdk/core openbb_sdk/sdk/provider -type f -name "pyproject.toml" -execdir sh -c '
    echo "Installing $(basename "$PWD")..."
    "$1" -m poetry install -C "${PWD}"
    if [ $? -ne 0 ]; then
        echo "Script terminated!"
        exit 1
    fi
' _ "$PYTHON_EXEC" {} +
