import argparse
from datetime import datetime, timedelta

import dateutil.parser
import flair
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
import requests

import config_terminal as cfg
from helper_funcs import clean_tweet, get_data


# ------------------------------------------------- INFERENCE -------------------------------------------------
def inference(l_args, s_ticker):
    parser = argparse.ArgumentParser(prog='infer',
                                     description="""Print quick sentiment inference from last tweets that contain
                                     the ticker. This model splits the text into character-level
                                     tokens and uses the DistilBERT model to make predictions. DistilBERT is a distilled
                                     version of the powerful BERT transformer model. Not only time period of these,
                                     but also frequency. [Source: Twitter]""")

    parser.add_argument('-n', "--num", action="store", dest="n_num", type=int, default=100, choices=range(10,101),
                        help='num of latest tweets to infer from.')

    (ns_parser, l_unknown_args) = parser.parse_known_args(l_args)

    if l_unknown_args:
        print(f"The following args couldn't be interpreted: {l_unknown_args}\n")
        return

    # Get tweets using Twitter API
    params = {
        'q': '$'+s_ticker,
        'tweet_mode': 'extended',
        'lang': 'en',
        'count': str(ns_parser.n_num)
    }

    # Request Twitter API
    response = requests.get('https://api.twitter.com/1.1/search/tweets.json',
                            params=params,
                            headers={'authorization': 'Bearer '+ cfg.API_TWITTER_BEARER_TOKEN})

    # Create dataframe
    df_tweets = pd.DataFrame()

    # Check that the API response was successful
    if response.status_code == 200:
        for tweet in response.json()['statuses']:
            row = get_data(tweet)
            df_tweets = df_tweets.append(row, ignore_index=True)

    # Load sentiment model
    sentiment_model = flair.models.TextClassifier.load('en-sentiment')
    print("")

    # We will append probability/sentiment preds later
    probs = []
    sentiments = []
    for s_tweet in df_tweets['text'].to_list():
        tweet = clean_tweet(s_tweet, s_ticker)

        # Make sentiment prediction
        sentence = flair.data.Sentence(tweet)
        sentiment_model.predict(sentence)

        # Extract sentiment prediction (POSITIVE/NEGATIVE) and confidence (0-1)
        probs.append(sentence.labels[0].score)
        sentiments.append(sentence.labels[0].value)

    # Add probability and sentiment predictions to tweets dataframe
    df_tweets['probability'] = probs
    df_tweets['sentiment'] = sentiments

    # Add sentiment estimation (probability positive for POSITIVE sentiment, and negative for NEGATIVE sentiment)
    df_tweets['sentiment_estimation'] = df_tweets.apply(lambda row: row['probability']*(-1, 1)[row['sentiment']=='POSITIVE'], axis=1).cumsum()
    # Cumulative sentiment_estimation
    df_tweets['prob_sen'] = df_tweets.apply(lambda row: row['probability']*(-1, 1)[row['sentiment']=='POSITIVE'], axis=1)

    # Percentage of confidence
    if df_tweets['sentiment_estimation'].values[-1] > 0:
        n_pos = df_tweets[df_tweets['prob_sen']>0]['prob_sen'].sum()
        n_pct = round(100*n_pos/df_tweets['probability'].sum())
    else:
        n_neg = abs(df_tweets[df_tweets['prob_sen']<0]['prob_sen'].sum())
        n_pct = round(100*n_neg/df_tweets['probability'].sum())

    # Parse tweets
    dt_from = dateutil.parser.parse(df_tweets['created_at'].values[-1])
    dt_to = dateutil.parser.parse(df_tweets['created_at'].values[0])
    print(f"From: {dt_from.strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"To:   {dt_to.strftime('%Y-%m-%d %H:%M:%S')}")

    print(f"{len(df_tweets)} tweets were analyzed.")
    dt_delta = (dt_to - dt_from)
    n_freq = dt_delta.total_seconds()/len(df_tweets)
    print(f"Frequency of approx 1 tweet every {round(n_freq)} seconds.")

    s_sen =  f"{('NEGATIVE', 'POSITIVE')[int(df_tweets['sentiment_estimation'].values[-1] > 0)]}"
    s_conf = f"{round(100*df_tweets['sentiment_estimation'].values[-1]/df_tweets['probability'].sum())}%"
    print(f"The sentiment of {s_ticker} is: {s_sen} ({s_conf})")
    print("")



# ------------------------------------------------- SENTIMENT -------------------------------------------------
def sentiment(l_args, s_ticker):
    parser = argparse.ArgumentParser(prog='sen',
                                     description="""Plot in-depth sentiment predicted from tweets from last days
                                     that contain pre-defined ticker. This model splits the text into character-level
                                     tokens and uses the DistilBERT model to make predictions. DistilBERT is a distilled
                                     version of the powerful BERT transformer model. Note that a big num of tweets extracted per
                                     hour in conjunction with a high number of days in the past, will make the
                                     algorithm take a long period of time to estimate sentiment. [Source: Twitter]""")

    # in reality this argument could be 100, but after testing it takes too long to compute which may not be acceptable
    parser.add_argument('-n', "--num", action="store", dest="n_tweets", type=int, default=10, choices=range(10,61),
                        help='num of tweets to extract per hour.')
    parser.add_argument('-d', "--days", action="store", dest="n_days_past", type=int, default=7, choices=range(1,8),
                        help='num of days in the past to extract tweets.')

    (ns_parser, l_unknown_args) = parser.parse_known_args(l_args)

    if l_unknown_args:
        print(f"The following args couldn't be interpreted: {l_unknown_args}\n")
        return

    # Setup API request params and headers
    headers = {'authorization': f'Bearer {cfg.API_TWITTER_BEARER_TOKEN}'}
    params = {
        'query': f'({s_ticker}) (lang:en)',
        'max_results': str(ns_parser.n_tweets),
        'tweet.fields': 'created_at,lang'
    }

    # Date format string required by twitter
    dtformat = '%Y-%m-%dT%H:%M:%SZ'

    # Algorithm to extract
    dt_recent = datetime.now()  - timedelta(seconds=20)
    dt_old = dt_recent - timedelta(days=ns_parser.n_days_past)
    print(f"From {dt_recent.date()} retrieving {ns_parser.n_tweets*24} tweets ({ns_parser.n_tweets} tweets/hour)")

    df_tweets = pd.DataFrame()
    while True:
        # Iterate until we haven't passed the old number of days
        if dt_recent < dt_old:
            break

        # Update past datetime
        dt_past = dt_recent - timedelta(minutes=60)

        if dt_past.day < dt_recent.day:
            print(f"From {dt_past.date()} retrieving {ns_parser.n_tweets*24} tweets ({ns_parser.n_tweets} tweets/hour)")

        # Assign from and to datetime parameters for the API
        params['start_time'] = dt_past.strftime(dtformat)
        params['end_time'] = dt_recent.strftime(dtformat)

        # Send API request
        response = requests.get('https://api.twitter.com/2/tweets/search/recent',
                                params=params,
                                headers=headers)

        # Update recent datetime
        dt_recent = dt_past

        # If response from API request is a success
        if response.status_code == 200:

            # Iteratively append our tweet data to our dataframe
            for tweet in response.json()['data']:
                row = get_data(tweet)
                df_tweets = df_tweets.append(row, ignore_index=True)

    # Load sentiment model
    print("")
    sentiment_model = flair.models.TextClassifier.load('en-sentiment');
    print("")

    # Append probability and sentiment preds later
    probs = []
    sentiments = []
    for s_tweet in df_tweets['text'].to_list():
        tweet = clean_tweet(s_tweet, s_ticker)

        # Make sentiment prediction
        sentence = flair.data.Sentence(tweet)
        sentiment_model.predict(sentence)

        # Extract sentiment prediction (POSITIVE/NEGATIVE) and confidence (0-1)
        probs.append(sentence.labels[0].score)
        sentiments.append(sentence.labels[0].value)

    # Add probability and sentiment predictions to tweets dataframe
    df_tweets['probability'] = probs
    df_tweets['sentiment'] = sentiments

    # Sort tweets per date
    df_tweets.sort_index(ascending=False, inplace=True)

    # Add sentiment estimation (probability positive for POSITIVE sentiment, and negative for NEGATIVE sentiment)
    df_tweets['sentiment_estimation'] = df_tweets.apply(lambda row: row['probability']*(-1, 1)[row['sentiment']=='POSITIVE'], axis=1).cumsum()
     # Cumulative sentiment_estimation
    df_tweets['prob_sen'] = df_tweets.apply(lambda row: row['probability']*(-1, 1)[row['sentiment']=='POSITIVE'], axis=1)

    # Percentage of confidence
    if df_tweets['sentiment_estimation'].values[-1] > 0:
        n_pos = df_tweets[df_tweets['prob_sen']>0]['prob_sen'].sum()
        n_pct = round(100*n_pos/df_tweets['probability'].sum())
    else:
        n_neg = abs(df_tweets[df_tweets['prob_sen']<0]['prob_sen'].sum())
        n_pct = round(100*n_neg/df_tweets['probability'].sum())
    s_sen =  f"{('NEGATIVE', 'POSITIVE')[int(df_tweets['sentiment_estimation'].values[-1] > 0)]}"

    #df_tweets.to_csv(r'notebooks/tweets.csv', index=False)
    df_tweets.reset_index(inplace=True)

    # Plotting
    plt.subplot(211)
    plt.title(f"Twitter's {s_ticker} sentiment over time is {s_sen} ({n_pct} %)")
    plt.plot(df_tweets.index, df_tweets['sentiment_estimation'].values, lw=3, c='cyan')
    plt.xlim(df_tweets.index[0], df_tweets.index[-1])
    plt.grid(b=True, which='major', color='#666666', linestyle='-', lw=1.5, alpha=0.5)
    plt.minorticks_on()
    plt.grid(b=True, which='minor', color='#999999', linestyle='-', alpha=0.2)
    plt.ylabel('Cumulative Sentiment')
    l_xticks = list()
    l_xlabels = list()
    l_xticks.append(0)
    l_xlabels.append(df_tweets['created_at'].values[0].split(' ')[0])
    n_day = datetime.strptime(df_tweets['created_at'].values[0], "%Y-%m-%d %H:%M:%S").day
    n_idx = 0
    n_next_idx = 0
    for n_next_idx, dt_created in enumerate(df_tweets['created_at']):
        if datetime.strptime(dt_created, "%Y-%m-%d %H:%M:%S").day > n_day:
            l_xticks.append(n_next_idx)
            l_xlabels.append(df_tweets['created_at'].values[n_next_idx].split(' ')[0])
            l_val_days = df_tweets['sentiment_estimation'].values[n_idx:n_next_idx]-df_tweets['sentiment_estimation'].values[n_idx]
            plt.plot(range(n_idx, n_next_idx), l_val_days, lw=3, c='tab:blue')
            n_day_avg = np.mean(l_val_days)
            if n_day_avg > 0:
                plt.hlines(n_day_avg, n_idx, n_next_idx, linewidth=2.5, linestyle='--', color='green', lw=3)
            else:
                plt.hlines(n_day_avg, n_idx, n_next_idx, linewidth=2.5, linestyle='--', color='red', lw=3)
            n_idx = n_next_idx
            n_day += 1
    l_val_days = df_tweets['sentiment_estimation'].values[n_idx:]-df_tweets['sentiment_estimation'].values[n_idx]
    plt.plot(range(n_idx, len(df_tweets)), l_val_days, lw=3, c='tab:blue')
    n_day_avg = np.mean(l_val_days)
    if n_day_avg > 0:
        plt.hlines(n_day_avg, n_idx, len(df_tweets), linewidth=2.5, linestyle='--', color='green', lw=3)
    else:
        plt.hlines(n_day_avg, n_idx, len(df_tweets), linewidth=2.5, linestyle='--', color='red', lw=3)
    l_xticks.append(len(df_tweets))
    datetime.strptime(dt_created, "%Y-%m-%d %H:%M:%S") + timedelta(days=1)
    l_xlabels.append(datetime.strftime(datetime.strptime(df_tweets['created_at'].values[len(df_tweets)-1], "%Y-%m-%d %H:%M:%S") + timedelta(days=1), "%Y-%m-%d"))
    plt.xticks(l_xticks, l_xlabels)
    plt.axhspan(plt.gca().get_ylim()[0], 0, facecolor='r', alpha=0.1)
    plt.axhspan(0, plt.gca().get_ylim()[1], facecolor='g', alpha=0.1)

    plt.subplot(212)
    plt.bar(df_tweets[df_tweets['prob_sen']>0].index, df_tweets[df_tweets['prob_sen']>0]['prob_sen'].values, color='green')
    plt.bar(df_tweets[df_tweets['prob_sen']<0].index, df_tweets[df_tweets['prob_sen']<0]['prob_sen'].values, color='red')
    for l_x in l_xticks[1:]:
        plt.vlines(l_x, -1, 1, linewidth=2, linestyle='--', color='k', lw=3)
    plt.xlim(df_tweets.index[0], df_tweets.index[-1])
    plt.xticks(l_xticks, l_xlabels)
    plt.grid(b=True, which='major', color='#666666', linestyle='-')
    plt.ylabel('Sentiment')
    plt.xlabel("Time")
    plt.show()
