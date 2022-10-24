# OpenBBTerminal Docker

These files create our docker images. To use docker read [this](openbb_terminal/DOCKER_README.md).

## Building the Docker Image

Building the Docker image can be done easily. The following steps allow users to create a docker
image on their local machine:

1. Enter the OpenBB directory `cd ~/OpenbbTerminal`
1. Open `docker/compose.env` and set `OPENBBTERMINAL_DOCKER_RELEASE_VERSION` to the desired version
1. Load the environment variables `bash compose/env`
1. Run the build script `bash docker/build.sh` 

**Note**: The `build.sh` script requires bash 5.0 or newer.
**Note**: If you have issues building on MacOs run the following commands:

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

The three docker files (`python.dockerfile`, `poetry-deps.dockerfile`, and `poetry.dockerfile`)
build off of each other to improving caching. A greater description of each stage is below

1. `python.dockerfile`: builds a docker image with a slim-bullseye python3.9 environment. It then
    labels the image and installs python and poetry.
2. `poetry-deps.dockerfile`: imports everything from the previous build, adds a label, and then
    install the poetry dependencies.
3. `poetry.dockerfile`: imports the poetry dependencies, adds its own label, and then starts an
    instance of the terminal

The `build.sh` file creates each of these images in the correct order, and populates the correct
arguments based on what is provided in `compose.env`.
