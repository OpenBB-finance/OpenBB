# Docker Advanced Settings

## Environment Variables

In order to pass your API keys to the docker container, they must first be set in a local file.  In the main repository, there is a file with predefined keys and terminal settings [setenv](gamestonk_terminal/docker/setenv).  This can be downloaded or created on your own

The file should contain something such as:
```
GT_API_KEY_FINANCIALMODELINGPREP="YOUR_KEY"
GT_API_REDDIT_CLIENT_ID="YOUR_KEY"
GT_API_REDDIT_CLIENT_SECRET="YOUR_KEY"
GT_API_REDDIT_USERNAME="YOUR_KEY"
GT_API_REDDIT_USER_AGENT=Python
GT_API_REDDIT_PASSWORD="YOUR_KEY"
GT_API_TWITTER_KEY="YOUR_KEY"
GT_API_TWITTER_SECRET_KEY="YOUR_KEY"
GT_FRED_API_KEY="YOUR_KEY"

HDF5_DISABLE_VERSION_CHECK=2

GTFF_ENABLE_PREDICT=True
GTFF_ENABLE_THOUGHTS_DAY=False
GTFF_USE_PROMPT_TOOLKIT=True
GTFF_USE_ION=True
```

In order to run the docker container with the environment variables, make sure to edit with whatever keys you have and then run the container (`path/to/file`) should be replaced with wherever this file was created).  If you have downloaded the entire repository and your current directory is `GamestonkTerminal`, then the path would be `docker/setenv`

```
docker run -it --rm --env-file=path/to/file ghcr.io/gamestonkterminal/gst-poetry:latest
```

## X-Server

In order to display plots in the docker container, we need to configure our XServer.  Users familiar with Docker can just set the DISPLAY variable in their file described above.

For help setting up the X-Server, I will go through this now:

### Setting up X Quartz/X11

0. Install X Quartz from  https://www.xquartz.org/
1. With X Quartz open: go to Preferences -> Security and make sure both options are enabled.
![Screen Shot 2021-09-08 at 12 21 48 PM](https://user-images.githubusercontent.com/18151143/132548605-235d774b-9aa6-4a45-afcf-58fb775d376a.png)


### Adding the display for Docker

From the command prompt or terminal, run the following to add your local configuration to the list of allowed access control:
```bash
IP=$(ifconfig en1 | grep inet | awk '$1=="inet" {print $2}')
xhost + $IP
```

Now we can run the docker container, adding the display to the environment:
```bach
docker run -it --rm --env-file=path/to/file -e DISPLAY=$IP:0 ghcr.io/gamestonkterminal/gst-poetry:latest
```
This container will be able to display all the same plots as the terminal interface.
