---
title: Introduction to the Behavioural Analysis
keywords: "stocks, behaviour, analysis, ba, headlines, snews, wsb, watchlist, popular, spac, trending, stalking, bullbear, messages, inter, sentiment, Google, Twitter, Reddit, Stocktwits, SentimentInvestor, Cramer, Jim, mentions, regions, interest, queries, rise, trend, hist, jcrd, jctr"
date: "2022-05-23"
type: guides
status: publish
excerpt: "An Introduction to the Behavioural Analysis menu, within the Stocks menu."
geekdocCollapseSection: true
---
The Behavioural Analysis menu offers the user tools for gauging the overall public sentiment of a company online.
The complexity of the tools range from message board scrapers to deep learning algorithms for financial analysis and prediction.
Sentiment is particularly useful for momentum trading strategies, discovery, and general fundamental research.
Navigate into the menu from the <a href="https://openbb-finance.github.io/OpenBBTerminal/terminal/stocks/" target="_blank">Stocks</a> menu by entering, `ba`; or, using absolute paths from anywhere in the Terminal: `/stocks/ba`

<a target="_blank" href="https://user-images.githubusercontent.com/46355364/170242317-ae66ed0b-f2e8-4304-9231-ea833d01e0e2.png"><img alt="The Behavioural Analysis submenu" src="https://user-images.githubusercontent.com/46355364/170242317-ae66ed0b-f2e8-4304-9231-ea833d01e0e2.png"></a>

## How to use

The commands with <span style="color:#00AAFF">Light Blue</span> text, representing <a href="https://openbb-finance.github.io/OpenBBTerminal/terminal/#structure-of-the-openbb-terminal" target="_blank">commands</a>,
do not require a ticker, faded commands will turn light blue when there is a ticker loaded.

````
(🦋) /stocks/ba/ $ load gme

Loading Daily GME stock with starting period 2019-05-20 for analysis.

Datetime: 2022 May 23 12:13
Timezone: America/New_York
Currency: USD
Market:   CLOSED
Company:  GameStop Corporation

(🦋) /stocks/ba/ $ ?
````

<a target="_blank" href="https://user-images.githubusercontent.com/46355364/170242757-3e29f690-7d29-4fe2-9e14-889c43e3142e.png"><img alt="The Behavioural Analysis Menu with a loaded ticker" src="https://user-images.githubusercontent.com/46355364/170242757-3e29f690-7d29-4fe2-9e14-889c43e3142e.png"></a>

Some data sources will require a valid API key, which can be obtained for free and then set using the Keys menu.
To use all the features in this menu, obtain free API keys from these providers:

- <a href="https://finnhub.io/" target="_blank">Finnhub</a><br>
- <a href="https://developer.twitter.com/" target="_blank">Twitter</a><br>
- <a href="https://old.reddit.com/prefs/apps/" target="_blank">Reddit</a><br>
- <a href="https://sentimentinvestor.com/" target="_blank">Sentiment Investor</a><br>

See the <a href="https://openbb-finance.github.io/OpenBBTerminal/terminal/#accessing-other-sources-of-data-via-api-keys" target="_blank">Getting Started Guide</a>
for help setting API keys in the Terminal.

## Examples

As with every command, using the `-h` argument displays the help dialogue. Running the <a href="https://openbb-finance.github.io/OpenBBTerminal/terminal/common/behavioural_analysis/headlines/" target="_blank">headlines</a>
command returns the following:

````
(🦋) /stocks/ba/ $ headlines
````
<a target="_blank" href="https://user-images.githubusercontent.com/46355364/170244924-ffe6cd15-8d17-4690-bf44-d2b496dbc310.png"><img alt="headlines" src="https://user-images.githubusercontent.com/46355364/170244924-ffe6cd15-8d17-4690-bf44-d2b496dbc310.png"></a>

Alternatively, running the <a href="https://openbb-finance.github.io/OpenBBTerminal/terminal/common/behavioural_analysis/snews/" target="_blank">snews</a>
command returns the following:

````
(🦋) /stocks/ba/ $ snews
````

<a target="_blank" href="https://user-images.githubusercontent.com/46355364/170243359-9d1302f0-3394-4e05-8360-0e59a1cb6e54.png"><img alt="headlines" src="https://user-images.githubusercontent.com/46355364/170243359-9d1302f0-3394-4e05-8360-0e59a1cb6e54.png"></a>

The Reddit functions will return popular tickers and posts, or measure sentiment for a particular stock. An example
would be by looking at the threads that pop up on <a href="https://www.reddit.com/r/wallstreetbets/" target="_blank">/r/wallstreetbets</a>,
famous for the <a href="https://en.wikipedia.org/wiki/R/wallstreetbets" target="_blank">GameStop short squeeze</a>:

````
(🦋) /stocks/ba/ $ wsb

2022-05-23 10:00:12 - Daily Discussion Thread for May 23, 2022
https://old.reddit.com/r/wallstreetbets/comments/uvwq8z/daily_discussion_thread_for_may_23_2022/

                                 Reddit Submission                                 
┏━━━━━━━━━━━━━━━━┳━━━━━━━━━━━━━━━━━━┳━━━━━━━┳━━━━━━━━━━━━┳━━━━━━━━━━┳━━━━━━━━━━━━━┓
┃ Subreddit      ┃ Flair            ┃ Score ┃ # Comments ┃ Upvote % ┃ Awards      ┃
┡━━━━━━━━━━━━━━━━╇━━━━━━━━━━━━━━━━━━╇━━━━━━━╇━━━━━━━━━━━━╇━━━━━━━━━━╇━━━━━━━━━━━━━┩
│ wallstreetbets │ Daily Discussion │ 195   │ 9168       │ 88%      │ 3 Silver    │
│                │                  │       │            │          │ 2 Helpful   │
│                │                  │       │            │          │ 1 Wholesome │
│                │                  │       │            │          │ 1 Got the   │
└────────────────┴──────────────────┴───────┴────────────┴──────────┴─────────────┘

2022-05-21 11:34:21 - Most Anticipated Earnings Releases for the week beginning May 23rd, 2022
https://old.reddit.com/r/wallstreetbets/comments/uul9fs/most_anticipated_earnings_releases_for_the_week/

                                   Reddit Submission                                   
┏━━━━━━━━━━━━━━━━┳━━━━━━━━━━━━━━━━━┳━━━━━━━┳━━━━━━━━━━━━┳━━━━━━━━━━┳━━━━━━━━━━━━━━━━━━┓
┃ Subreddit      ┃ Flair           ┃ Score ┃ # Comments ┃ Upvote % ┃ Awards           ┃
┡━━━━━━━━━━━━━━━━╇━━━━━━━━━━━━━━━━━╇━━━━━━━╇━━━━━━━━━━━━╇━━━━━━━━━━╇━━━━━━━━━━━━━━━━━━┩
│ wallstreetbets │ Earnings Thread │ 960   │ 1325       │ 97%      │ 1 Silver         │
│                │                 │       │            │          │ 5 Helpful        │
│                │                 │       │            │          │ 3 Wholesome      │
│                │                 │       │            │          │ 1 Take My Energy │
│                │                 │       │            │          │ 1 Sne            │
└────────────────┴─────────────────┴───────┴────────────┴──────────┴──────────────────┘

<continues>
````

The Behavioural Analysis menu also has the ability to scan for sentiment on multiple platforms including Twitter and Google
with <a href="https://openbb-finance.github.io/OpenBBTerminal/terminal/common/behavioural_analysis/sentiment/" target="_blank">sentiment</a>,
<a href="https://openbb-finance.github.io/OpenBBTerminal/terminal/common/behavioural_analysis/infer/" target="_blank">infer</a>
and <a href="https://openbb-finance.github.io/OpenBBTerminal/terminal/common/behavioural_analysis/queries/" target="_blank">queries</a>.
````
(🦋) /stocks/ba/ $ sentiment -c
From 2022-05-23 retrieving 360 tweets (15 tweets/hour)
From 2022-05-22 retrieving 360 tweets (15 tweets/hour)
From 2022-05-21 retrieving 360 tweets (15 tweets/hour)
From 2022-05-20 retrieving 360 tweets (15 tweets/hour)
From 2022-05-19 retrieving 360 tweets (15 tweets/hour)
From 2022-05-18 retrieving 360 tweets (15 tweets/hour)
From 2022-05-17 retrieving 360 tweets (15 tweets/hour)

(🦋) /stocks/ba/ $ infer
From: 2022-05-23 18:21:12
To:   2022-05-23 18:30:36
100 tweets were analyzed.
Frequency of approx 1 tweet every 6 seconds.
The summed compound sentiment of GME is: 18.42
The average compound sentiment of GME is: 0.18
Of the last 100 tweets, 41.00 % had a higher positive sentiment
Of the last 100 tweets, 19.00 % had a higher negative sentiment

(🦋) /stocks/ba/ $ queries

 Top GME's related queries 
┏━━━━━━━━━━━━━━━━━┳━━━━━━━┓
┃ query           ┃ value ┃
┡━━━━━━━━━━━━━━━━━╇━━━━━━━┩
│ stock gme       │ 100%  │
├─────────────────┼───────┤
│ amc             │ 29%   │
├─────────────────┼───────┤
│ amc stock       │ 24%   │
├─────────────────┼───────┤
│ gme price       │ 23%   │
├─────────────────┼───────┤
│ gme stock price │ 14%   │
├─────────────────┼───────┤
│ gme share       │ 7%    │
├─────────────────┼───────┤
│ gme share price │ 6%    │
├─────────────────┼───────┤
│ reddit          │ 6%    │
├─────────────────┼───────┤
│ gme reddit      │ 6%    │
├─────────────────┼───────┤
│ bb              │ 5%    │
└─────────────────┴───────┘
````
The <a href="https://openbb-finance.github.io/OpenBBTerminal/terminal/common/behavioural_analysis/sentiment/" target="_blank">sentiment</a>
command returns the following:

<a target="_blank" href="https://user-images.githubusercontent.com/46355364/170243539-1ea3fc6a-d7ec-4991-a6bb-ed5879753328.png"><img alt="sentiment" src="https://user-images.githubusercontent.com/46355364/170243539-1ea3fc6a-d7ec-4991-a6bb-ed5879753328.png"></a>

More advanced techniques can also be applied by using tools from <a href="https://sentimentinvestor.com" target="_blank">Sentiment Investor</a>
that analyzes millions of messages to show the most talked about stocks by hour. This has the ability to show the
most trending tickers with <a href="https://openbb-finance.github.io/OpenBBTerminal/terminal/common/behavioural_analysis/trend/" target="_blank">trend</a> and historical sentiment data with 
<a href="https://openbb-finance.github.io/OpenBBTerminal/terminal/common/behavioural_analysis/hist/" target="_blank">hist</a>.

````
(🦋) /stocks/ba/ $ trend

Most trending stocks at 2022-05-23 00:00 
┏━━━━━━━━┳━━━━━━━┳━━━━━━━━┳━━━━━━┳━━━━━━┓
┃ TICKER ┃ TOTAL ┃ LIKES  ┃ RHI  ┃ AHI  ┃
┡━━━━━━━━╇━━━━━━━╇━━━━━━━━╇━━━━━━╇━━━━━━┩
│ SPY    │ 89.00 │ 43.00  │ 1.22 │ 1.26 │
├────────┼───────┼────────┼──────┼──────┤
│ AMC    │ 80.00 │ 155.00 │ 1.07 │ 1.18 │
├────────┼───────┼────────┼──────┼──────┤
│ TSLA   │ 80.00 │ 78.00  │ 1.07 │ 1.34 │
├────────┼───────┼────────┼──────┼──────┤
│ BTC    │ 62.00 │ 74.00  │ 1.14 │ 1.09 │
├────────┼───────┼────────┼──────┼──────┤
│ NIO    │ 50.00 │ 14.00  │ 1.17 │ 1.15 │
├────────┼───────┼────────┼──────┼──────┤
│ AAPL   │ 28.00 │ 4.00   │ 0.66 │ 0.75 │
├────────┼───────┼────────┼──────┼──────┤
│ AMD    │ 26.00 │ 59.00  │ 0.57 │ 0.61 │
├────────┼───────┼────────┼──────┼──────┤
│ NVAX   │ 13.00 │ 4.00   │ 0.47 │ 0.40 │
├────────┼───────┼────────┼──────┼──────┤
│ NVDA   │ 12.00 │ 11.00  │ 0.45 │ 0.47 │
├────────┼───────┼────────┼──────┼──────┤
│ DIS    │ 12.00 │ 1.00   │ 0.69 │ 0.44 │
└────────┴───────┴────────┴──────┴──────┘

(🦋) /stocks/ba/ $ hist -s 2022-05-01
````

<a target="_blank" href="https://user-images.githubusercontent.com/46355364/170243719-fccf414b-3a89-4776-88de-e30f4eb34f89.png"><img alt="hist" src="https://user-images.githubusercontent.com/46355364/170243719-fccf414b-3a89-4776-88de-e30f4eb34f89.png"></a>

Inspired by the Twitter user, <a href="https://twitter.com/CramerTracker" target="_blank">@cramertracker</a>, the final
two features follow (CNBC Talking Head) Jim Cramer stock recommendations as satire that rings true.

````
(🦋) /stocks/ba/ $ jcdr

                         Jim Cramer Recommendations for 05/19                         
┏━━━━━━━━━━━━━━━━━━━━━━━━┳━━━━━━━━┳━━━━━━━━┳━━━━━━━━━━━┳━━━━━━━━━━━━┳━━━━━━━━━━━━━━━━┓
┃ Company                ┃ Symbol ┃ Price  ┃ LastPrice ┃ Change (%) ┃ Recommendation ┃
┡━━━━━━━━━━━━━━━━━━━━━━━━╇━━━━━━━━╇━━━━━━━━╇━━━━━━━━━━━╇━━━━━━━━━━━━╇━━━━━━━━━━━━━━━━┩
│ Apple                  │ AAPL   │ 137.35 │ 142.38    │ 3.53       │ Buy            │
├────────────────────────┼────────┼────────┼───────────┼────────────┼────────────────┤
│ AeroVironment          │ AVAV   │ 85.35  │ 85.49     │ 0.16       │ Buy            │
├────────────────────────┼────────┼────────┼───────────┼────────────┼────────────────┤
│ Alibaba                │ BABA   │ 87.69  │ 87.04     │ -0.75      │ Sell           │
├────────────────────────┼────────┼────────┼───────────┼────────────┼────────────────┤
│ Constellation Energy   │ CEG    │ 57.23  │ 56.92     │ -0.54      │ Buy            │
├────────────────────────┼────────┼────────┼───────────┼────────────┼────────────────┤
│ Costco                 │ COST   │ 422.93 │ 427.93    │ 1.17       │ Buy            │
├────────────────────────┼────────┼────────┼───────────┼────────────┼────────────────┤
│ DraftKings             │ DKNG   │ 14.15  │ 13.89     │ -1.87      │ Buy            │
├────────────────────────┼────────┼────────┼───────────┼────────────┼────────────────┤
│ Lockheed Martin        │ LMT    │ 425.62 │ 433.71    │ 1.87       │ Buy            │
├────────────────────────┼────────┼────────┼───────────┼────────────┼────────────────┤
│ Cloudflare             │ NET    │ 58.00  │ 56.92     │ -1.90      │ Buy            │
├────────────────────────┼────────┼────────┼───────────┼────────────┼────────────────┤
│ Northrop Grumman       │ NOC    │ 448.50 │ 456.57    │ 1.77       │ Buy            │
├────────────────────────┼────────┼────────┼───────────┼────────────┼────────────────┤
│ NVIDIA                 │ NVDA   │ 171.24 │ 168.29    │ -1.75      │ Buy            │
├────────────────────────┼────────┼────────┼───────────┼────────────┼────────────────┤
│ Palo Alto Networks     │ PANW   │ 436.37 │ 502.69    │ 13.19      │ Buy            │
├────────────────────────┼────────┼────────┼───────────┼────────────┼────────────────┤
│ PLBY Group             │ PLBY   │ 9.06   │ 9.26      │ 2.16       │ Sell           │
├────────────────────────┼────────┼────────┼───────────┼────────────┼────────────────┤
│ Raytheon Technologies  │ RTX    │ 90.25  │ 91.87     │ 1.76       │ Buy            │
├────────────────────────┼────────┼────────┼───────────┼────────────┼────────────────┤
│ SoFi Technologies      │ SOFI   │ 7.75   │ 7.30      │ -6.16      │ Buy            │
└────────────────────────┴────────┴────────┴───────────┴────────────┴────────────────┘
````
<a target="_blank" href="https://user-images.githubusercontent.com/46355364/170243863-f95dc515-c0d7-4ede-964d-f6ba41aec743.png"><img alt="Jim Cramer historical recommendations for $DKNG" src="https://user-images.githubusercontent.com/46355364/170243863-f95dc515-c0d7-4ede-964d-f6ba41aec743.png"></a>
