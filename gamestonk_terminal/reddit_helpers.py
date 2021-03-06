from datetime import datetime, timedelta
import re
from holidays import US as holidaysUS
from prettytable import PrettyTable


def print_and_record_reddit_post(submissions_dict, submission):
    # Refactor data
    s_datetime = datetime.utcfromtimestamp(submission.created_utc).strftime(
        "%d/%m/%Y %H:%M:%S"
    )
    s_link = f"https://old.reddit.com{submission.permalink}"
    s_all_awards = ""
    for award in submission.all_awardings:
        s_all_awards += f"{award['count']} {award['name']}\n"
    s_all_awards = s_all_awards[:-2]
    # Create dictionary with data to construct dataframe allows to save data
    submissions_dict[submission.id] = {
        "created_utc": s_datetime,
        "subreddit": submission.subreddit,
        "link_flair_text": submission.link_flair_text,
        "title": submission.title,
        "score": submission.score,
        "link": s_link,
        "num_comments": submission.num_comments,
        "upvote_ratio": submission.upvote_ratio,
        "awards": s_all_awards,
    }
    # Print post data collected so far
    print(f"{s_datetime} - {submission.title}")
    print(f"{s_link}")
    t_post = PrettyTable(
        ["Subreddit", "Flair", "Score", "# Comments", "Upvote %", "Awards"]
    )
    t_post.add_row(
        [
            submission.subreddit,
            submission.link_flair_text,
            submission.score,
            submission.num_comments,
            f"{round(100 * submission.upvote_ratio)}%",
            s_all_awards,
        ]
    )
    print(t_post)
    print("\n")


def get_last_time_market_was_open(dt):
    # Check if it is a weekend
    if dt.date().weekday() > 4:
        dt = get_last_time_market_was_open(dt - timedelta(hours=24))

    # Check if it is a holiday
    if dt.strftime("%Y-%m-%d") in holidaysUS():
        dt = get_last_time_market_was_open(dt - timedelta(hours=24))

    dt = dt.replace(hour=21, minute=0, second=0)

    return dt


def find_tickers(submission):
    ls_text = list()
    ls_text.append(submission.selftext)
    ls_text.append(submission.title)

    submission.comments.replace_more(limit=0)
    for comment in submission.comments.list():
        ls_text.append(comment.body)

    l_tickers_found = list()
    for s_text in ls_text:
        for s_ticker in set(re.findall(r"([A-Z]{3,5} )", s_text)):
            l_tickers_found.append(s_ticker.strip())

    return l_tickers_found

