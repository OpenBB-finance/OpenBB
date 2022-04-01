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
docker run -it --rm --env-file=path/to/setenv ghcr.io/OpenBBTerminal/gst-poetry:latest
```

## Display

In order to display plots in the docker container, we can configure our XServer.

Users familiar with Docker and X-Server can set the `DISPLAY` variable in the file [setenv](/docker/setenv) described
above. If you use this approach remember to add `:0` at the end of your inet address. E.g. `DISPLAY=192.168.1.155:0`.

### X-Server

For help setting up the X-Server, I will go through this now:

#### Setting up X Quartz/X11

0. Install X Quartz from <https://www.xquartz.org/>
1. With X Quartz open: go to Preferences -> Security and make sure both options are enabled.
   ![Screen Shot 2021-09-08 at 12 21 48 PM](https://user-images.githubusercontent.com/18151143/132548605-235d774b-9aa6-4a45-afcf-58fb775d376a.png)

#### Adding the display for Docker

From the command prompt or terminal, run the following to add your local configuration to the list of allowed access control:

```bash
IP=$(ifconfig | grep inet | grep -v -e "127.0.0.1" | awk '$1=="inet" {print $2}')
xhost + $IP
```

Now we can run the docker container, adding the display to the environment:

```bach
docker run -it --rm --env-file=path/to/setenv -e DISPLAY=$IP:0 ghcr.io/OpenBBTerminal/gst-poetry:latest
```

This container will be able to display all the same plots as the terminal interface.
