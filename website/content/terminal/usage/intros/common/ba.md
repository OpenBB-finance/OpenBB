---
title: Behavioural Analysis
keywords: [stocks, behaviour, analysis, ba, headlines, snews, wsb, watchlist, popular, spac, trending, stalking, bullbear, messages, inter, sentiment, Google, Twitter, Reddit, Stocktwits, SentimentInvestor, Cramer, Jim, mentions, regions, interest, queries, rise, trend, hist, jcrd, jctr, how to, examples]
description: Learn the basics of the Behavioural Analysis menu. It offers the user tools for gauging the overall public sentiment of a company online. The complexity of the tools range from message board scrapers to deep learning algorithms for financial analysis and prediction.
---

import HeadTitle from '@site/src/components/General/HeadTitle.tsx';

<HeadTitle title="Behavioural Analysis - Terminal | OpenBB Docs" />

The Behavioural Analysis menu offers the user tools for gauging the overall public sentiment of a company online. The complexity of the tools range from message board scrapers to deep learning algorithms for financial analysis and prediction. Sentiment is particularly useful for momentum trading strategies, discovery, and general fundamental research. Navigate into the menu from the <a href="/terminal/usage/intros/stocks/" target="_blank" rel="noreferrer noopener">Stocks</a> menu by entering, `ba`; or, using absolute paths from anywhere in the Terminal: `/stocks/ba`

<img width="800" alt="image" src="https://user-images.githubusercontent.com/46355364/218975466-a52343f6-9f43-4ecc-88ac-f47afbd7f128.png"></img>

### How to use

Some data sources will require a valid API key, which can be obtained for free and then set using the [Keys menu](https://docs.openbb.co/terminal/usage/guides/api-keys). As with every command, using the `-h` argument displays the help dialogue. Running the <a href="/terminal/reference/stocks/ba/headlines/" target="_blank" rel="noreferrer noopener">headlines</a> command returns the following:

```
(🦋) /stocks/ba/ $ headlines
```

<img alt="headlines" src="https://user-images.githubusercontent.com/46355364/170244924-ffe6cd15-8d17-4690-bf44-d2b496dbc310.png"></img>

Alternatively, running the <a href="/terminal/reference/stocks/ba/snews/" target="_blank" rel="noreferrer noopener">snews</a> command returns the following:

```
(🦋) /stocks/ba/ $ snews
```

<img alt="headlines" src="https://user-images.githubusercontent.com/46355364/170243359-9d1302f0-3394-4e05-8360-0e59a1cb6e54.png"></img>

The Reddit functions will return popular tickers and posts, or measure sentiment for a particular stock. An example would be by looking at the threads that pop up on <a href="https://www.reddit.com/r/wallstreetbets/" target="_blank" rel="noreferrer noopener">/r/wallstreetbets</a>, famous for the <a href="https://en.wikipedia.org/wiki/R/wallstreetbets" target="_blank" rel="noreferrer noopener">GameStop short squeeze</a>:

```
(🦋) /stocks/ba/ $ wsb

2022-05-23 10:00:12 - Daily Discussion Thread for May 23, 2022
https://old.reddit.com/r/wallstreetbets/comments/uvwq8z/daily_discussion_thread_for_may_23_2022/

Reddit Submission

| Subreddit      | Flair            | Score | # Comments | Upvote % | Awards      |
| -------------- | ---------------- | ----- | ---------- | -------- | ----------- |
| wallstreetbets | Daily Discussion | 195   | 9168       | 88%      | 3 Silver    |
|                |                  |       |            |          | 2 Helpful   |
|                |                  |       |            |          | 1 Wholesome |
|                |                  |       |            |          | 1 Got the   |

2022-05-21 11:34:21 - Most Anticipated Earnings Releases for the week beginning
May 23rd, 2022
https://old.reddit.com/r/wallstreetbets/comments/uul9fs/most_anticipated_earnings_releases_for_the_week/

Reddit Submission

| Subreddit      | Flair           | Score | # Comments | Upvote % | Awards           |
| -------------- | --------------- | ----- | ---------- | -------- | ---------------- |
| wallstreetbets | Earnings Thread | 960   | 1325       | 97%      | 1 Silver         |
|                |                 |       |            |          | 5 Helpful        |
|                |                 |       |            |          | 3 Wholesome      |
|                |                 |       |            |          | 1 Take My Energy |
|                |                 |       |            |          | 1 Sne            |
```

The Behavioural Analysis menu also has the ability to scan for sentiment on multiple platforms including Twitter and Google with <a href="/terminal/reference/stocks/ba/sentiment/" target="_blank" rel="noreferrer noopener">sentiment</a>, <a href="/terminal/reference/stocks/ba/infer/" target="_blank" rel="noreferrer noopener">infer</a> and <a href="/terminal/reference/stocks/ba/queries/" target="_blank" rel="noreferrer noopener">queries</a>.

```
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

| query           | value |
|-----------------|-------|
| stock gme       | 100%  |
| amc             | 29%   |
| amc stock       | 24%   |
| gme price       | 23%   |
| gme stock price | 14%   |
| gme share       | 7%    |
| gme share price | 6%    |
| reddit          | 6%    |
| gme reddit      | 6%    |
| bb              | 5%    |
```

The <a href="/terminal/reference/stocks/ba/sentiment/" target="_blank" rel="noreferrer noopener">sentiment</a> command returns the following:

<img alt="sentiment" src="https://user-images.githubusercontent.com/46355364/170243539-1ea3fc6a-d7ec-4991-a6bb-ed5879753328.png"></img>
