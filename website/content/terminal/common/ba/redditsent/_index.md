```txt
usage: redditsent [-s {relevance,hot,top,new,comments}] [-c COMPANY] [--subreddits SUBREDDITS] [-l LIMIT]
                   [-t {hour,day,week,month,year,all}] [-f] [-g] [-h] [--export EXPORT]
```

Determine general Reddit sentiment about a ticker. [Source: Reddit]

```txt
optional arguments:
  -s {relevance,hot,top,new,comments}, --sort {relevance,hot,top,new,comments}
                        search sorting type
  -c COMPANY, --company COMPANY
                        explicit name of company to search for, will override ticker symbol
  --subreddits SUBREDDITS
                        comma-separated list of subreddits to search
  -l LIMIT, --limit LIMIT
                        how many posts to gather from each subreddit
  -t {hour,day,week,month,year,all}, --time {hour,day,week,month,year,all}
                        time period to get posts from -- all, year, month, week, or day; defaults to week
  --full                enable comprehensive search
  -g, --graphic         display graphic
  -d, --display         Print table of sentiment values
  -h, --help            show this help message
  --export EXPORT       Export raw data into csv, json, xlsx and figure into png, jpg, pdf, svg
```

Example:

```txt
redditsent -c Google --subreddits tech,stocks --full
Searching through subreddits for posts.
100%|█████████████████████████████████████████████████████████████████████████| 2/2 [00:01<00:00,  1.84it/s]
Analyzing each post...
100%|███████████████████████████████████████████████████████████████████████| 10/10 [00:04<00:00,  2.07it/s]
Sentiment Analysis for Google is 0.7552
```
