# Docker Advanced Settings

## Environment Variables

In order to pass your API keys to the docker container, they must first be set in a local file. In the main repository,
there is a file with predefined keys and terminal settings [setenv](/docker/setenv). This can be downloaded or created
on your own

The file should contain something such as:

```bash
DISPLAY=

OPENBB_API_KEY_FINANCIALMODELINGPREP=qwerty123456
...
OPENBB_API_POLYGON_KEY=qwerty123456
OPENBB_API_FRED_KEY=qwerty123456

HDF5_DISABLE_VERSION_CHECK=2

OPENBB_ENABLE_PREDICT=True
OPENBB_ENABLE_THOUGHTS_DAY=False
OPENBB_USE_PROMPT_TOOLKIT=True
OPENBB_USE_ION=True
```

where 'qwerty123456' corresponds to each individual API key. Note:

1. Unlike API keys in [config_terminal](/openbb_terminal/config_terminal.py), these keys **DO NOT** use " ".
2. This file is sensible to white spaces. Therefore, make sure there isn't an additional white space at the end of the
   key, otherwise it won't work.

In order to run the docker container with the environment variables, make sure to edit with whatever keys you have and
then run the container (`path/to/setenv`) should be replaced with wherever this file was created). If you have
downloaded the entire repository and your current directory is `OpenBBTerminal`, then the path would be `docker/setenv`

```bash
docker run -it --rm --env-file=path/to/setenv ghcr.io/openbb-finance/openbbterminal-poetry:latest
```

## Display

In order to display plots in the docker container, we can use IPC socket to connect Desktop.

Add this setting to 'setenv' file .

```bash
OPENBB_BACKEND=Qt5Agg
```

And run the following commands.

```bash
xhost +local:
docker run -it --rm --name openbb --env-file=./setenv -e DISPLAY=$DISPLAY -v /tmp/.X11-unix:/tmp/.X11-unix ghcr.io/openbb-finance/openbbterminal-poetry:latest
xhost -local:
```

This container will be able to display all the same plots as the terminal interface.
