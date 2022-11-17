```
usage: spacc [-l N_LIMIT] [-p] [-h]
```

Print other users SPACs announcements under subreddit 'SPACs'. [Source: Reddit]

```
optional arguments:
  -l N_LIMIT, --limit N_LIMIT
                        limit of posts with SPACs retrieved (default: 10)
  -p, --popular         popular flag, if true the posts retrieved are based on score rather than time (default: False)
  -h, --help            show this help message (default: False)
```

Example:

```
2022 Feb 16, 10:43 (🦋) /stocks/ba/ $ spacc
2022-02-16 11:35:01 - I scraped r/SPACs for the top ticker mentions in the last 24H. Here are the results (Wednesday February 16, 2022)
https://old.reddit.com/r/SPACs/comments/sttsnl/i_scraped_rspacs_for_the_top_ticker_mentions_in/

2022-02-16 09:26:19 - PPGH Gogoro confirms that it is expected to list overseas in the first quarter of this year
https://old.reddit.com/r/SPACs/comments/strs9m/ppgh_gogoro_confirms_that_it_is_expected_to_list/

2022-02-16 08:00:16 - Announcements x Daily Discussion for Wednesday, February 16, 2022
https://old.reddit.com/r/SPACs/comments/stqhci/announcements_x_daily_discussion_for_wednesday/

2022-02-15 15:10:40 - Did IBKR resolve my SPAC redemptions wrongly?
https://old.reddit.com/r/SPACs/comments/st52xb/did_ibkr_resolve_my_spac_redemptions_wrongly/

The following stock tickers have been mentioned more than once across the previous SPACs:
8 CCAC, 6 IBKR, 3 CLBT, 3 SLDP, 2 VIAC, 2 CND
```
