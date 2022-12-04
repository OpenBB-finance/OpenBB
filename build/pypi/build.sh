#!/bin/sh

# BUILD `openbb_terminal/.env`
OPENBB_LOGGING_COMMIT_HASH="sha:$(git rev-parse --short=8 HEAD)"
OPENBB_LOGGING_APP_NAME="gst_packaged_pypi"
echo "OPENBB_LOGGING_APP_NAME='${OPENBB_LOGGING_APP_NAME}'" > openbb_terminal/.env
echo "OPENBB_LOGGING_COMMIT_HASH=${OPENBB_LOGGING_COMMIT_HASH}" >> openbb_terminal/.env

poetry publish --build