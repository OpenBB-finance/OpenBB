#!/bin/bash
set -e

# This script is used to remove artifacts left from the conda build process

# Ensure that conda is installed
if ! command -v conda &> /dev/null
then
    echo "conda could not be found"
    exit
fi

# Ensure that the obb conda environment exists
if ! conda env list | grep -q "obb"
then
    echo "The obb conda environment does not exist"
    echo "Create it by running:"
    echo "conda env create -n obb --file build/conda/conda-3-10-env.yaml"
    exit
fi

# Ensure that the obb conda environment is activated
if [[ -z "$CONDA_PREFIX" ]] || [[ "$CONDA_PREFIX" != *"obb" ]]
then
    echo "The obb conda environment is not activated"
    echo "Activate it by running 'conda activate obb'"
    exit
fi

# Remove build artifacts
find "$(dirname "$(dirname "$(which python)")")"/lib/python*/site-packages \
     -maxdepth 2 -name direct_url.json \
     -exec rm -f {} +

# Say goodbye
echo "Done"
