```
usage: historical [-t TICKER] [-s [{date,value}]] [-d [{asc,desc}]] [-h] [{sentiment,AHI,RHI,SGP}]
```

Sentiment Investor analyzes data from four major social media platforms to generate hourly metrics on over 2,000 stocks. Sentiment provides volume and sentiment metrics powered by proprietary NLP models.

The historical command plots the past week of data for a selected metric, one of:

AHI (Absolute Hype Index)
---
AHI is a measure of how much people are talking about a stock on social media.
It is calculated by dividing the total number of mentions for the chosen stock on a social network by the mean number of mentions any stock receives on that social medium.

RHI (Relative Hype Index)
---
RHI is a measure of whether people are talking about a stock more or less than usual, calculated by dividing the mean AHI for the past day by the mean AHI for for the past week for that stock.

Sentiment Score
---
Sentiment score is the percentage of people talking positively about the stock.
For each social network the number of positive posts/comments is divided by the total number of both positive and negative posts/comments.

SGP (Standard General Perception)
---
SGP is a measure of whether people are more or less positive about a stock than usual. It is calculated by averaging the past day of sentiment values and then dividing it by the average of the past week of sentiment values.

```
positional arguments:
  {sentiment,AHI,RHI,SGP}
                        the metric to plot

optional arguments:
  -t TICKER, --ticker TICKER
                        ticker for which to fetch data
  -s [{date,value}], --sort [{date,value}]
                        the parameter to sort output table by
  -d [{asc,desc}], --direction [{asc,desc}]
                        the direction to sort the output table
  -h, --help            show this help message
```

<img width="1183" alt="Captura de ecrã 2021-08-06, às 22 00 22" src="https://user-images.githubusercontent.com/25267873/128570628-162d036e-37f8-48cc-bd8d-b5e79141db5d.png">

![sentiment_score](https://user-images.githubusercontent.com/25267873/128570642-b40df4d1-e95e-4e7e-846c-9f38d34c75cd.png)
