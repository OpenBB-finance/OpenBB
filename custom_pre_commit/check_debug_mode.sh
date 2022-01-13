#!/usr/bin/env bash

set -e

VAR="$(grep DEBUG_MODE gamestonk_terminal/config_terminal.py)"

if [[ $VAR != "DEBUG_MODE = False" ]]
then
    exit 1
fi