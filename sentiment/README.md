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
  * [bullbear](#bullbear)
    - estimate quick sentiment from last 30 messages on board 
  * [messages](#messages)
    - output up to the 30 last messages on the board
  * [trending](#trending)
    - trending stocks
  * [stalker](#stalker)
    - stalk stocktwits user's last messages

[TWITTER](#TWITTER)
  * [infer](#infer)
    - infer about stock's sentiment from latest tweets
  * [sentiment](#sentiment)
    - in-depth sentiment prediction from tweets over time
   
[GOOGLE](#GOOGLE)
  * [mentions](#mentions)
    - interest over time based on stock's mentions
  * [regions](#regions)
    - regions that show highest interest in stock
  * [queries](#queries)
    - top related queries with this stock
  * [rise](#rise)
    - top rising related queries with stock


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
  * -p : popular flag, if true the posts retrieved are based on score rather than time. Default False.

<img width="959" alt="spac_c" src="https://user-images.githubusercontent.com/25267873/108612072-d34d7400-73dc-11eb-850c-36a4e7224918.png">


# STOCKTWITS <a name="STOCKTWITS"></a>

## bullbear <a name="bullbear"></a>
```
usage: bullbear [-t S_TICKER]
```
Print bullbear sentiment based on last 30 messages on the board. Also prints the watchlist_count. [Source: Stocktwits]
  * -t : ticker to gather sentiment from.
                                     
<img width="934" alt="sentiment" src="https://user-images.githubusercontent.com/25267873/108612307-42c46300-73df-11eb-9cec-253c8fb6d62f.png">


## messages <a name="messages"></a>
```
usage: messages [-t S_TICKER] [-l N_LIM]
```
Print up to 30 of the last messages on the board. [Source: Stocktwits]
  * -t : get board messages from this ticker. Default pre-loaded.
  * -l : limit messages shown. Default 30.

<img width="958" alt="messages" src="https://user-images.githubusercontent.com/25267873/108612310-448e2680-73df-11eb-8fa8-b619c6269742.png">


## trending <a name="trending"></a>
```
usage: trending
```
Stocks trending. [Source: Stocktwits]

<img width="956" alt="trending" src="https://user-images.githubusercontent.com/25267873/108612311-4526bd00-73df-11eb-840b-18829fcecdd3.png">


## stalker <a name="stalker"></a>
```
usage: stalker [-u S_USER] [-l N_LIM]
```
Print up to the last 30 messages of a user. [Source: Stocktwits]
  * -u : username. Default newsfilter.
  * -l : limit messages shown. Default 30.

<img width="943" alt="stalker" src="https://user-images.githubusercontent.com/25267873/108612309-435cf980-73df-11eb-92c9-e9f15f966d8e.png">


# TWITTER <a name="TWITTER"></a>

## infer <a name="infer"></a>
```
usage: infer [-n N_NUM]
```
Print quick sentiment inference from last tweets that contain the ticker. This model splits the text into character-level tokens and uses the DistilBERT model to make predictions. DistilBERT is a distilled version of the powerful BERT transformer model. Not only time period of these, but also frequency. Inspired by https://towardsdatascience.com/sentiment-analysis-for-stock-price-prediction-in-python-bed40c65d178. [Source: Twitter]
  * -n : num of latest tweets to infer from. Default 100.

<img width="948" alt="Captura de ecrã 2021-02-22, às 00 18 22" src="https://user-images.githubusercontent.com/25267873/108643679-808abf80-74a3-11eb-9b50-899be0a4799f.png">

## sentiment <a name="sentiment"></a>
```
usage: sentiment [-n N_NUM] [-d N_DAYS_PAST]
```
Plot in-depth sentiment extracted from tweets from last days that contain pre-defined ticker. This model splits the text into character-level tokens and uses the DistilBERT model to make predictions. DistilBERT is a distilled version of the powerful BERT transformer model. Note that a big num of tweets extracted per hour in conjunction with a high number of days in the past, will make the algorithm take a long period of time to estimate sentiment. Inspired by https://towardsdatascience.com/sentiment-analysis-for-stock-price-prediction-in-python-bed40c65d178. [Source: Twitter] 
  * -n : num of tweets to extract per hour. Default 100.
  * -d : num of days in the past to extract tweets. Default 7.

<img width="949" alt="Captura de ecrã 2021-02-22, às 00 15 20" src="https://user-images.githubusercontent.com/25267873/108643678-7ff22900-74a3-11eb-9bea-54f84ffe42e1.png">

![nvda](https://user-images.githubusercontent.com/25267873/108643604-2ab61780-74a3-11eb-950b-ba0bbec8293e.png)

Additional examples:

![bb](https://user-images.githubusercontent.com/25267873/108643608-2db10800-74a3-11eb-838c-3db6ec2be9aa.png)

![tsla](https://user-images.githubusercontent.com/25267873/108643609-2e499e80-74a3-11eb-8fa8-489ea15b27c4.png)


# GOOGLE

## mentions <a name="mentions"></a>
```
usage: mentions [-s S_START]
```
Plot weekly bars of stock's interest over time. other users watchlist. [Source: Google]
  * -s : starting date (format YYYY-MM-DD) from when we are interested in stock's mentions. Default: the one provided in main menu.

![gme](https://user-images.githubusercontent.com/25267873/108776894-e9813e80-755a-11eb-8b7e-654124c0ef8f.png)


## regions <a name="regions"></a>
```
usage: regions [-n N_NUM]
```
Plot bars of regions based on stock's interest. [Source: Google]
  * -n : number of regions to plot that show highest interest. Default 10.

![regions](https://user-images.githubusercontent.com/25267873/108776889-e8e8a800-755a-11eb-8bcc-fcf7b6156f50.png)


## queries <a name="queries"></a>
```
usage: queries [-n N_NUM]
```
Print top related queries with this stock's query. [Source: Google]
  * -n : number of top related queries to print. Default 10.

<img width="937" alt="Captura de ecrã 2021-02-22, às 22 15 16" src="https://user-images.githubusercontent.com/25267873/108777341-91970780-755b-11eb-985e-819285688eea.png">


## rise <a name="rise"></a>
```
usage: rise [-n N_NUM]
```
Print top rising related queries with this stock's query. [Source: Google]
  * -n : number of top rising related queries to print. Default 10.

<img width="934" alt="Captura de ecrã 2021-02-22, às 22 21 21" src="https://user-images.githubusercontent.com/25267873/108777814-4f21fa80-755c-11eb-96da-0327c9a0da57.png">


