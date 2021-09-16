```
usage: metrics [-h] [ticker]
```

Sentiment Investor analyzes data from four major social media platforms to
generate hourly metrics on over 2,000 stocks. Sentiment provides volume and
sentiment metrics powered by proprietary NLP models.

The metrics command prints the following realtime metrics:

AHI (Absolute Hype Index)
---
AHI is a measure of how much people are talking about a stock on social media.
It is calculated by dividing the total number of mentions for the chosen stock
on a social network by the mean number of mentions any stock receives on that
social medium.

RHI (Relative Hype Index)
---
RHI is a measure of whether people are talking about a stock more or less than
usual, calculated by dividing the mean AHI for the past day by the mean AHI for
for the past week for that stock.

Sentiment Score
---
Sentiment score is the percentage of people talking positively about the stock.
For each social network the number of positive posts/comments is divided by the
total number of both positive and negative posts/comments.

SGP (Standard General Perception)
---
SGP is a measure of whether people are more or less positive about a stock than
usual. It is calculated by averaging the past day of sentiment values and then
dividing it by the average of the past week of sentiment values.

```
positional arguments:
  ticker      ticker to use instead of the loaded one

optional arguments:
  -h, --help  show this help message
```

<img width="1183" alt="Captura de ecrã 2021-08-06, às 22 00 05" src="https://user-images.githubusercontent.com/25267873/128570641-29bab43b-b4bb-4c40-8467-ea366c903b7e.png">
