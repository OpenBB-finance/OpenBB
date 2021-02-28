#!/bin/bash

function find_pyfiles() {
    for f in $(find . -type f -iname '*.py'); do
        if [ ! -e "$(dirname $f)/.circuitpython.skip" ]; then
            echo "$f"
        fi
    done
}

find_pyfiles | xargs pylint
