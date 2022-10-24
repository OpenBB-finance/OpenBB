#!/bin/sh

poetry run python -m build.pypi.make_env_file
poetry build
poetry publish