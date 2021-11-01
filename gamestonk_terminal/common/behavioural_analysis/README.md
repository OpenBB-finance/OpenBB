# BEHAVIOURAL ANALYSIS

This menu aims to extrapolate behavioural analysis regarding a pre-loaded ticker, and the usage of the following
commands along with an example will be exploited below.

* [finbrain](#finbrain)
  * sentiment from 15+ major news headlines
* [stats](#stats)
  * sentiment stats including comparison with sector

[REDDIT](#REDDIT)

* [wsb](#wsb)
  * show what WSB gang is up to in subreddit wallstreetbets
* [watchlist](#watchlist)
  * show other users watchlist
* [popular](#popular)
  * show popular tickers
* [spac_c](#spac_c)
  * show other users spacs announcements from subreddit SPACs community
* [spac](#spac)
  * show other users spacs announcements from other subs

[STOCKTWITS](#STOCKTWITS)

* [bullbear](#bullbear)
  * estimate quick sentiment from last 30 messages on board
* [messages](#messages)
  * output up to the 30 last messages on the board
* [trending](#trending)
  * trending stocks
* [stalker](#stalker)
  * stalk stocktwits user's last messages

[TWITTER](#TWITTER)

* [infer](#infer)
  * infer about stock's sentiment from latest tweets
* [sentiment](#sentiment)
  * in-depth sentiment prediction from tweets over time

[GOOGLE](#GOOGLE)

* [mentions](#mentions)
  * interest over time based on stock's mentions
* [regions](#regions)
  * regions that show highest interest in stock
* [queries](#queries)
  * top related queries with this stock
* [rise](#rise)
  * top rising related queries with stock

[SENTIMENT INVESTOR](#SENTIMENTINVESTOR)

* [metrics](#metrics)
  * core social sentiment metrics for this stock
* [social](#social)
  * social media figures for stock popularity
* [historical](#historical)
  * plot the past week of data for a selected metric

## finbrain <a name="finbrain"></a>

```text
usage: finbrain
```

FinBrain collects the news headlines from 15+ major financial news sources on a daily basis and analyzes them to
generate sentiment scores for more than 4500 US stocks. FinBrain Technologies develops deep learning algorithms for
financial analysis and prediction, which currently serves traders from more than 150 countries all around the world.
[Source: See <https://finbrain.tech>]

![finbrain2](https://user-images.githubusercontent.com/25267873/111629515-49c97000-87e9-11eb-92a6-a9eebb4b4bd9.png)

<img width="986" alt="Finbrain" src="https://user-images.githubusercontent.com/25267873/111629542-4fbf5100-87e9-11eb-8d5d-96faa8d3fca4.png">

## stats <a name="stats"></a>

```text
usage: stats
```

Sentiment stats which displays buzz, news score, articles last week, articles weekly average, bullish vs bearish
percentages, sector average bullish percentage, and sector average news score. [Source: <https://finnhub.io>]

<img width="1003" alt="Stats" src="https://user-images.githubusercontent.com/25267873/116888922-e9b94c80-ac23-11eb-959e-be24c79488a3.png">

# REDDIT <a name="REDDIT"></a>

## wsb <a name="wsb"></a>

```text
usage: wsb [-l N_LIMIT] [-n]
```

Print what WSB gang are up to in subreddit wallstreetbets. [Source: Reddit]

* -l : limit of posts to print. Default 10.
* -n : new flag, if true the posts retrieved are based on being more recent rather than their score. Default False.

<img width="947" alt="wsb" src="https://user-images.githubusercontent.com/25267873/108612074-d5afce00-73dc-11eb-80ca-8ecfad12020c.png">

## watchlist <a name="watchlist"></a>

```text
usage: watchlist [-l N_LIMIT]
```

Print other users watchlist. [Source: Reddit]

* -l : limit of posts to print. Default 5.

<img width="941" alt="watchlist" src="https://user-images.githubusercontent.com/25267873/108920576-caeb7800-762c-11eb-937c-94ecbb65d119.png">

## popular <a name="popular"></a>

```text
usage: popular [-l N_LIMIT] [-s S_SUBREDDIT] [-d N_DAYS]
```

Print latest popular tickers. [Source: Reddit]

* -l : limit of posts retrieved per sub reddit. Default 50.
* -s : subreddits to look for tickers, e.g. pennystocks,stocks. Default: pennystocks, RobinHoodPennyStocks, Daytrading,
StockMarket, stocks, investing, wallstreetbets.

<img width="948" alt="popular" src="https://user-images.githubusercontent.com/25267873/108917846-4dbe0400-7628-11eb-821e-9fda97a6d9cd.png">

## spac_c <a name="spac_c"></a>

```text
usage: spac_c [-l N_LIMIT] [-p]
```

Print other users SPACs announcement under subreddit 'SPACs'. [Source: Reddit]

* -l : limit of posts with SPACs retrieved. Default 10.
* -p : popular flag, if true the posts retrieved are based on score rather than time. Default False.

<img width="936" alt="spac_c" src="https://user-images.githubusercontent.com/25267873/108920571-c8891e00-762c-11eb-8da8-e2b775bc7109.png">

## spac <a name="spac"></a>

```text
usage: spac [-h] [-l N_LIMIT] [-d N_DAYS]
```

Print other users SPACs announcement under subreddit 'SPACs'. [Source: Reddit]

* -l : limit of posts with SPACs retrieved. Default 5.

<img width="939" alt="spac" src="https://user-images.githubusercontent.com/25267873/108920696-04bc7e80-762d-11eb-896b-1b1c19903584.png">

# STOCKTWITS <a name="STOCKTWITS"></a>

## bullbear <a name="bullbear"></a>

```text
usage: bullbear [-t S_TICKER]
```

Print bullbear sentiment based on last 30 messages on the board. Also prints the watchlist_count. [Source: Stocktwits]

* -t : ticker to gather sentiment from.

<img width="934" alt="sentiment" src="https://user-images.githubusercontent.com/25267873/108612307-42c46300-73df-11eb-9cec-253c8fb6d62f.png">

## messages <a name="messages"></a>

```text
usage: messages [-t S_TICKER] [-l N_LIM]
```

Print up to 30 of the last messages on the board. [Source: Stocktwits]

* -t : get board messages from this ticker. Default pre-loaded.
* -l : limit messages shown. Default 30.

<img width="958" alt="messages" src="https://user-images.githubusercontent.com/25267873/108612310-448e2680-73df-11eb-8fa8-b619c6269742.png">

## trending <a name="trending"></a>

```text
usage: trending
```

Stocks trending. [Source: Stocktwits]

<img width="956" alt="trending" src="https://user-images.githubusercontent.com/25267873/108612311-4526bd00-73df-11eb-840b-18829fcecdd3.png">

## stalker <a name="stalker"></a>

```text
usage: stalker [-u S_USER] [-l N_LIM]
```

Print up to the last 30 messages of a user. [Source: Stocktwits]

* -u : username. Default newsfilter.
* -l : limit messages shown. Default 30.

<img width="943" alt="stalker" src="https://user-images.githubusercontent.com/25267873/108612309-435cf980-73df-11eb-92c9-e9f15f966d8e.png">

# TWITTER <a name="TWITTER"></a>

Uses VADER sentiment.  VADER (Valence Aware Dictionary and sEntiment Reasoner) is a lexicon and rule-based sentiment
analysis tool that is specifically attuned to sentiments expressed in social media.

The output of VADER analysis :

```text
The compound score is computed by summing the valence scores of each word in the lexicon, adjusted according to the
rules, and then normalized to be between -1 (most extreme negative) and +1 (most extreme positive). This is the most
useful metric if you want a single unidimensional measure of sentiment for a given sentence. Calling it a 'normalized,
 weighted composite score' is accurate.
```

A sample tweet is shown below along with what the VADER polarity scores are.

```text
Have some $SENS  🚀🏆\n👉FDA approval coming very soon, 👉News is out, amazing test results. \n👉Very high short
interest rate. \n👉Major short squeeze coming. \n\n$amc $gme $nakd $ctrm $tsla $aapl $oeg $aht $bbby $bb $fsr $spce
 https://t.co/B0cPhufpA2'
```

This gives the following scores:

```python
created_at                                  Thu Jun 03 20:37:54
text          Have some $SENS  🚀🏆\n👉FDA approval coming very...
sentiment                                                 0.872
positive                                                  0.177
negative                                                      0
neutral                                                   0.823
```

Note that both functions use twitters v2 endpoint, which only gives 7 days of historical data.  It also requires at
least 10 tweets be pulled.

## infer <a name="infer"></a>

```text
usage: infer [-n N_NUM]
```

Print quick sentiment inference from last tweets that contain the ticker. This model splits the text into
character-level tokens and uses theVADER model to make predictions.

* -n : num of latest tweets to infer from. Default 100.

## sentiment <a name="sentiment"></a>

```text
usage: sentiment [-n N_NUM] [-d N_DAYS_PAST]
```

Plot in-depth sentiment extracted from tweets from last days that contain pre-defined ticker. This model splits the
text into character-level tokens and uses the VADER model to make predictions.

* -n : num of tweets to extract per hour. Default 15.
* -d : num of days in the past to extract tweets. Default 6.  Max 6

# GOOGLE

## mentions <a name="mentions"></a>

```text
usage: mentions [-s S_START]
```

Plot weekly bars of stock's interest over time. other users watchlist. [Source: Google]

* -s : starting date (format YYYY-MM-DD) from when we are interested in stock's mentions. Default: the one provided
in main menu.

![gme](https://user-images.githubusercontent.com/25267873/108776894-e9813e80-755a-11eb-8b7e-654124c0ef8f.png)

## regions <a name="regions"></a>

```text
usage: regions [-n N_NUM]
```

Plot bars of regions based on stock's interest. [Source: Google]

* -n : number of regions to plot that show highest interest. Default 10.

![regions](https://user-images.githubusercontent.com/25267873/108776889-e8e8a800-755a-11eb-8bcc-fcf7b6156f50.png)

## queries <a name="queries"></a>

```text
usage: queries [-n N_NUM]
```

Print top related queries with this stock's query. [Source: Google]

* -n : number of top related queries to print. Default 10.

<img width="937" alt="Queries" src="https://user-images.githubusercontent.com/25267873/108777341-91970780-755b-11eb-985e-819285688eea.png">

## rise <a name="rise"></a>

```text
usage: rise [-n N_NUM]
```

Print top rising related queries with this stock's query. [Source: Google]

* -n : number of top rising related queries to print. Default 10.

<img width="934" alt="Rise" src="https://user-images.githubusercontent.com/25267873/108777814-4f21fa80-755c-11eb-96da-0327c9a0da57.png">

# SENTIMENTINVESTOR

> **[Sentiment Investor](https://sentimentinvestor.com)** analyzes data from four major social media platforms to
> generate hourly metrics on over 2,000 stocks. Sentiment provides volume and
> sentiment metrics powered by proprietary NLP models.

## Metric definitions

### AHI (Absolute Hype Index) <a name="AHI"></a>

AHI is a measure of how much people are talking about a stock on social media.
It is calculated by dividing the total number of mentions for the chosen stock
on a social network by the mean number of mentions any stock receives on that
social medium.

### RHI (Relative Hype Index) <a name="RHI"></a>

RHI is a measure of whether people are talking about a stock more or less than
usual, calculated by dividing the mean AHI for the past day by the mean AHI for
for the past week for that stock.

### Sentiment Score <a name="sentiment"></a>

Sentiment score is the percentage of people talking positively about the stock.
For each social network the number of positive posts/comments is divided by the
total number of both positive and negative posts/comments.

### SGP (Standard General Perception) <a name="SGP"></a>

SGP is a measure of whether people are more or less positive about a stock than
usual. It is calculated by averaging the past day of sentiment values and then
dividing it by the average of the past week of sentiment values.

## metrics <a name="metrics"></a>

```text
usage: metrics [-h] [ticker]
```

The `metrics` command presents the four core metrics provided by Sentiment Investor,
including AHI, RHI, sentiment and SGP, as described above.

Optional arguments:

* [optional, positional] ticker
  ticker to use instead of the loaded one
* `-h`, `--help`
  show this help message

Example output:

![`metrics NFLX` command output](https://user-images.githubusercontent.com/8385172/127154566-1af3c274-c521-426b-8580-2ae714c2c1ca.png)

## social <a name="social"></a>

```text
usage: social [-h] [ticker]
```

The `social` command prints the raw data for a given stock, including the number
of mentions it has received on social media in the last hour and the sentiment
score of those comments.

Optional arguments:

* [optional, positional] ticker
  ticker to use instead of the loaded one
* `-h`, `--help`
  show this help message

Example output:

![`social AAPL` command output](https://user-images.githubusercontent.com/8385172/127154775-13b1a81d-f5d2-4768-bf7e-bca8886f6d24.png)

## historical <a name="historical"></a>

```text
usage: historical [-t TICKER] [-s [{date,value}]] [-d [{asc,desc}]] [-h] [{sentiment,AHI,RHI,SGP}]
```

The `historical` command plots the past week of data for a selected
SentimentInvestor core metric, one of:
[AHI](#ahi), [RHI](#ahi), [sentiment](#sentiment) or [SGP](#SGP).
It also outputs a sorted table of the mean value for that metric for each day.

Positional arguments:

* one of `sentiment`, `AHI`, `RHI` or `SGP`
   (optional) the metric to plot (default: `sentiment`)

Optional arguments:

* `-t`, `--ticker TICKER`
   ticker for which to fetch data
* `-s`, `--sort [{date,value}]`
   the parameter to sort output table by
* `-d`, `--direction [{asc,desc}]`
   the direction to sort the output table
* `-h`, `--help`
   show this help message

Example output:

![`historical -t GME RHI` plot output](https://user-images.githubusercontent.com/8385172/126782509-bfc21dbb-2fe6-4cd4-a384-018eb41ac8f3.png)

![`historical -t NFLX -s value -d asc RHI` command output](https://user-images.githubusercontent.com/8385172/127157236-7818a635-4394-4372-9673-2834b32811af.png)
