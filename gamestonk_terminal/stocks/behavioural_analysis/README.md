# BEHAVIOURAL ANALYSIS

This menu aims to extrapolate behavioural analysis regarding a pre-loaded ticker, and the usage of the following commands along with an example will be exploited below.

[FINBRAIN](#FINBRAIN)
  * [finbrain](#finbrain)
     - sentiment from 15+ major news headlines
  * [stats](#stats)
     - sentiment stats including comparison with sector

[REDDIT](#REDDIT)
  * [wsb](#wsb)
    - show what WSB gang is up to in subreddit wallstreetbets
  * [watchlist](#watchlist)
    - show other users watchlist
  * [popular](#popular)
    - show popular tickers
  * [spac_c](#spac_c)
    - show other users spacs announcements from subreddit SPACs community
  * [spac](#spac)
    - show other users spacs announcements from other subs

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

[SENTIMENT INVESTOR](#SENTIMENT-INVESTOR)
  * [metrics](#metrics)
    - core social sentiment metrics for this stock
  * [social](#social)
    - social media figures for stock popularity
  * [historical](#historical)
    - plot the past week of data for a selected metric


# FINBRAIN <a name="FINBRAIN"></a>

## finbrain <a name="finbrain"></a>
```
usage: finbrain
```
FinBrain collects the news headlines from 15+ major financial news sources on a daily basis and analyzes them to generate sentiment scores for more than 4500 US stocks. FinBrain Technologies develops deep learning algorithms for financial analysis and prediction, which currently serves traders from more than 150 countries all around the world. [Source: See https://finbrain.tech]

![finbrain2](https://user-images.githubusercontent.com/25267873/111629515-49c97000-87e9-11eb-92a6-a9eebb4b4bd9.png)

<img width="986" alt="Captura de ecrã 2021-03-18, às 12 53 31" src="https://user-images.githubusercontent.com/25267873/111629542-4fbf5100-87e9-11eb-8d5d-96faa8d3fca4.png">


## stats <a name="stats"></a>
```
usage: stats
```
Sentiment stats which displays buzz, news score, articles last week, articles weekly average, bullish vs bearish percentages, sector average bullish percentage, and sector average news score. [Source: https://finnhub.io]

<img width="1003" alt="Captura de ecrã 2021-05-03, às 15 26 09" src="https://user-images.githubusercontent.com/25267873/116888922-e9b94c80-ac23-11eb-959e-be24c79488a3.png">


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

<img width="941" alt="watchlist" src="https://user-images.githubusercontent.com/25267873/108920576-caeb7800-762c-11eb-937c-94ecbb65d119.png">


## popular <a name="popular"></a>
```
usage: popular [-l N_LIMIT] [-s S_SUBREDDIT] [-d N_DAYS]
```
Print latest popular tickers. [Source: Reddit]
  * -l : limit of posts retrieved per sub reddit. Default 50.
  * -s : subreddits to look for tickers, e.g. pennystocks,stocks. Default: pennystocks, RobinHoodPennyStocks, Daytrading, StockMarket, stocks, investing, wallstreetbets.

<img width="948" alt="popular" src="https://user-images.githubusercontent.com/25267873/108917846-4dbe0400-7628-11eb-821e-9fda97a6d9cd.png">


## spac_c <a name="spac_c"></a>
```
usage: spac_c [-l N_LIMIT] [-p]
```
Print other users SPACs announcement under subreddit 'SPACs'. [Source: Reddit]
  * -l : limit of posts with SPACs retrieved. Default 10.
  * -p : popular flag, if true the posts retrieved are based on score rather than time. Default False.

<img width="936" alt="spac_c" src="https://user-images.githubusercontent.com/25267873/108920571-c8891e00-762c-11eb-8da8-e2b775bc7109.png">


## spac <a name="spac"></a>
```
usage: spac [-h] [-l N_LIMIT] [-d N_DAYS]
```
Print other users SPACs announcement under subreddit 'SPACs'. [Source: Reddit]
  * -l : limit of posts with SPACs retrieved. Default 5.

<img width="939" alt="spac" src="https://user-images.githubusercontent.com/25267873/108920696-04bc7e80-762d-11eb-896b-1b1c19903584.png">


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
Print quick sentiment inference from last tweets that contain the ticker. This model splits the text into character-level tokens and uses theVADER model to make predictions.
  * -n : num of latest tweets to infer from. Default 100.

<img width="901" alt="Captura de ecrã 2021-08-06, às 21 49 29" src="https://user-images.githubusercontent.com/25267873/128569570-7bec34ee-e024-4add-ab94-29df23af04ca.png">


## sentiment <a name="sentiment"></a>
```
usage: sentiment [-n N_NUM] [-d N_DAYS_PAST]
```
Plot in-depth sentiment extracted from tweets from last days that contain pre-defined ticker. This model splits the text into character-level tokens and uses the VADER model to make predictions.
  * -n : num of tweets to extract per hour. Default 15.
  * -d : num of days in the past to extract tweets. Default 6. Max 6


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

# SENTIMENT INVESTOR  <a name="SENTIMENT-INVESTOR"></a>

## metrics <a name="metrics"></a>
```
usage: metrics [ticker]
```
The `metrics` command presents the four core metrics provided by Sentiment Investor. Sentiment Investor analyzes data from four major social media platforms to generate hourly metrics on over 2,000 stocks. Sentiment provides volume and sentiment metrics powered by proprietary NLP models. These metrics include:

**AHI (Absolute Hype Index)** is a measure of how much people are talking about a stock on social media. It is calculated by dividing the total number of mentions for the chosen stock on a social network by the mean number of mentions any stock receives on that social medium.

**RHI (Relative Hype Index)** is a measure of whether people are talking about a stock more or less than usual, calculated by dividing the mean AHI for the past day by the mean AHI for for the past week for that stock.

**Sentiment Score** is the percentage of people talking positively about the stock. For each social network the number of positive posts/comments is divided by the total number of both positive and negative posts/comments.

**SGP (Standard General Perception)** is a measure of whether people are more or less positive about a stock than usual. It is calculated by averaging the past day of sentiment values and then dividing it by the average of the past week of sentiment values.

  * -t : ticker to use instead of the loaded one.

<img width="1183" alt="Captura de ecrã 2021-08-06, às 22 00 05" src="https://user-images.githubusercontent.com/25267873/128570641-29bab43b-b4bb-4c40-8467-ea366c903b7e.png">


## social <a name="social"></a>
```
usage: social [ticker]
```

The `social` command prints the raw data for a given stock, including the number of mentions it has received on social media in the last hour and the sentiment score of those comments. Sentiment Investor analyzes data from four major social media platforms to generate hourly metrics on over 2,000 stocks. Sentiment provides volume and sentiment metrics powered by proprietary NLP models.

  * -t : ticker to use instead of the loaded one.

<img width="1186" alt="Captura de ecrã 2021-08-06, às 22 00 15" src="https://user-images.githubusercontent.com/25267873/128570633-14bf8855-59ad-4ba2-a116-777b299c083c.png">


## historical <a name="historical"></a>
```
usage: historical [-t TICKER] [-s [{date,value}]] [-d [{asc,desc}]] [-h] [{sentiment,AHI,RHI,SGP}]
```

The `historical` command plots the past week of data for a selected SentimentInvestor core metric. Sentiment Investor analyzes data from four major social media platforms to generate hourly metrics on over 2,000 stocks. Sentiment provides volume and sentiment metrics powered by proprietary NLP models. These core metrics include:

**AHI (Absolute Hype Index)** is a measure of how much people are talking about a stock on social media. It is calculated by dividing the total number of mentions for the chosen stock on a social network by the mean number of mentions any stock receives on that social medium.

**RHI (Relative Hype Index)** is a measure of whether people are talking about a stock more or less than usual, calculated by dividing the mean AHI for the past day by the mean AHI for for the past week for that stock.

**Sentiment Score** is the percentage of people talking positively about the stock. For each social network the number of positive posts/comments is divided by the total number of both positive and negative posts/comments.

**SGP (Standard General Perception)** is a measure of whether people are more or less positive about a stock than usual. It is calculated by averaging the past day of sentiment values and then dividing it by the average of the past week of sentiment values.


It also outputs a sorted table of the mean value for that metric for each day.


  * -m : one of `sentiment`, `AHI`, `RHI` or `SGP`
  * -t : ticker for which to fetch data
  * -s : the parameter to sort output table by
  * -d : the direction to sort the output table

<img width="1183" alt="Captura de ecrã 2021-08-06, às 22 00 22" src="https://user-images.githubusercontent.com/25267873/128570628-162d036e-37f8-48cc-bd8d-b5e79141db5d.png">

![sentiment_score](https://user-images.githubusercontent.com/25267873/128570642-b40df4d1-e95e-4e7e-846c-9f38d34c75cd.png)
