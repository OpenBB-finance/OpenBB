# MARKET SENTIMENT

This menu aims to extrapolate market's sentiment regarding a pre-loaded ticker, and the usage of the following commands along with an example will be exploited below.

[REDDIT](#REDDIT)
  * [wsb](#wsb)
    - show what WSB gang is up to in subreddit wallstreetbets
  * [watchlist](#watchlist)
    - show other users watchlist
  * [popular](#popular)
    - show popular tickers
  * [spac](#spac)
    - show other users spacs announcements
  * [spac_c](#spac_c)
    - show other users spacs announcements from subreddit SPACs

[STOCKTWITS](#STOCKTWITS)
  * [sentiment](#sentiment)
    - estimate quick sentiment from last 30 messages on board 
  * [messages](#messages)
    - output up to the 30 last messages on the board
  * [trending](#trending)
    - trending stocks
  * [stalker](#stalker)
    - stalk stocktwits user's last messages


# REDDIT <a name="REDDIT"></a>

## wsb <a name="wsb"></a>
```
usage: wsb [-l N_LIMIT] [-n]
```
Print what WSB gang are up to in subreddit wallstreetbets. [Source: Reddit]
  * -l : limit of posts to print. Default 10.
  * -n : new flag, if true the posts retrieved are based on being more recent rather than their score. Default False.

<img width="947" alt="wsb" src="https://user-images.githubusercontent.com/25267873/108612074-d5afce00-73dc-11eb-80ca-8ecfad12020c.png">


## watchlist <a name="watchlist"></a>
```
usage: watchlist [-l N_LIMIT]
```
Print other users watchlist. [Source: Reddit]
  * -l : limit of posts to print. Default 5.

<img width="931" alt="watchlist" src="https://user-images.githubusercontent.com/25267873/108612073-d5173780-73dc-11eb-9757-0f135f43f21e.png">


## popular <a name="popular"></a>


## spac <a name="spac"></a>


## spac_c <a name="spac_c"></a>
```
usage: spac_c [-l N_LIMIT] [-p]
```
Print other users SPACs announcement under subreddit 'SPACs'. [Source: Reddit]
  * -l : limit of posts with SPACs retrieved. Default 10.
  * -p : popular flag, if true the posts retrieved are based on score rather than time. Default false.

<img width="959" alt="spac_c" src="https://user-images.githubusercontent.com/25267873/108612072-d34d7400-73dc-11eb-850c-36a4e7224918.png">


# STOCKTWITS <a name="STOCKTWITS"></a>

## sentiment <a name="sentiment"></a>

## messages <a name="messages"></a>

## trending <a name="trending"></a>

## stalker <a name="stalker"></a>
