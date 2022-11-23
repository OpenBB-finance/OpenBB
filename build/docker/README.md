# OpenBBTerminal Docker

These files create our docker images. To use docker read [this](openbb_terminal/DOCKER_README.md).

## Building the Docker Image

Building the Docker image can be done easily. The following steps allow users to create a docker
image on their local machine:

1. Enter the OpenBB directory `cd ~/OpenbbTerminal`
1. Open `docker/compose.env` and set `OPENBBTERMINAL_DOCKER_RELEASE_VERSION` to the desired version
1. Load the environment variables `bash compose/env`
1. Run the build script `bash docker/build.sh` 

### Important Notes

1. The `build.sh` script requires bash 5.0 or newer.
1. We currently build without developer dependnencies such as pytest. If you want to develop using
   this image please open `poetry.dockerfile` and replace `RUN poetry install --no-dev` with 
   `RUN poetry install`
1. If you have issues building on MacOs run the following commands:

    - `export DOCKER_BUILDKIT=0`
    - `export COMPOSE_DOCKER_CLI_BUILD=0`

## Testing the Docker Image

Integration and unit tests can be run on the new docker image. Before running either set of tests
you need to start up an image with:

- `docker run -it --rm ghcr.io/[BUILD_NAME]`

Leave the terminal open and then navigate docker desktop. Find the currently running image and
select `open in terminal`. Now:

- For integration tests run: `poetry run python terminal.py scripts -t`
- For unit tests run `poetry run pytest tests/`

## Setup Explanation

The `compose.env` file is responsible for loading in the correct environment variables before a
session begins. Once this is done the `build.sh` file creates a docker image with the appropriate
tag. The `poetry.dockerfile` is the file used to create the image. It has enhanced caching by
building in three stages. The stages are described below.

- python: this stage creates a new `python:3.9-slim-bullseye` image. Slim-buster is a small linux
  distro that comes with a lot of the functionality we need. We then set environment variables.
  This image will only be reran when there is a new version of `python:3.9-slim-bullseye` or when
  the environment variables are updated (there is almost never a reason to update them).
- poetry-deps: this stage installs necessary apt packages like curl and git, and then installs
  poetry. This will be reran whenever dependencies change, or whenever `python` has been rerun.
- poetry: this takes the build from `poetry-deps` and then copies the terminal files into it. Then
  this image runs the terminal. This image will be rebuilt every time files are changed in the
  terminal or when `poetry-deps` has been rerun, however; this is not an issue because it builds 
  quickly.
