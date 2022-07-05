```
usage: twitter [-l N] [-s {date,user_name,status,retweet_count,like_count}] [--descend] [--export {csv,json,xlsx}] [-h]
```

Show last 10 tweets for given coin. You can display only N number of tweets with --limit parameter. You can sort data by date, user_name, status,
retweet_count, like_count --sort parameter and also with --descend flag to sort descending. Displays: date, user_name, status, retweet_count, like_count

```
optional arguments:
  -l N, --limit N     Limit of records (default: 10)
  -s {date,user_name,status,retweet_count,like_count}, --sort {date,user_name,status,retweet_count,like_count}
                        Sort by given column. Default: date (default: date)
  --descend             Flag to sort in descending order (lowest first) (default: False)
  --export {csv,json,xlsx}
                        Export dataframe data to csv,json,xlsx file (default: )
  -h, --help            show this help message (default: False)
```

Example:
```
2022 Feb 15, 07:49 (✨) /crypto/dd/ $ twitter
                                                               Twitter Timeline
┌────────────┬────────────────┬──────────────────────────────────────────────────────────────────────────────────┬───────────────┬────────────┐
│ date       │ user_name      │ status                                                                           │ retweet_count │ like_count │
├────────────┼────────────────┼──────────────────────────────────────────────────────────────────────────────────┼───────────────┼────────────┤
│ 2021-10-27 │ bitcoincoreorg │ Bitcoin Core 0.20.2 (backports) was released It is available from                │ 67            │ 153        │
│ 10:55:48   │                │ https://t.co/ea0sMBjrp2 Release mail: https://t.co/KahVJFcZ9d                    │               │            │
├────────────┼────────────────┼──────────────────────────────────────────────────────────────────────────────────┼───────────────┼────────────┤
│ 2021-09-13 │ bitcoincoreorg │ Bitcoin Core 22.0 was released! It is available from https://t.co/WpMuMaejz1     │ 366           │ 1065       │
│ 22:01:09   │                │ Release mail: https://t.co/ZvZKXZ0iLD                                            │               │            │
├────────────┼────────────────┼──────────────────────────────────────────────────────────────────────────────────┼───────────────┼────────────┤
│ 2021-07-20 │ LukeDashjr     │ PSA: @BitcoinCoreOrg (#Bitcoin Core) is NOT soliciting or performing closed      │ 88            │ 0          │
│ 21:51:31   │                │ testing of any beta or other software.If you get an email inviting you, be       │               │            │
│            │                │ aware it is spam and their "testing version" is almost certainly malware.Note:   │               │            │
│            │                │ the "From" on emails is NOT secure and faked.                                    │               │            │
├────────────┼────────────────┼──────────────────────────────────────────────────────────────────────────────────┼───────────────┼────────────┤
│ 2021-07-03 │ bitcoincoreorg │ A reminder that Bitcoin Core is available for download worldwide through         │ 192           │ 577        │
│ 08:25:13   │                │ https://t.co/WpMuMaejz1 . It is also available through BitTorrent.               │               │            │
├────────────┼────────────────┼──────────────────────────────────────────────────────────────────────────────────┼───────────────┼────────────┤
│ 2021-06-03 │ pwuille        │ In version 0.21 @bitcoincoreorg added support for Tor V3:                        │ 73            │ 0          │
│ 17:16:25   │                │ https://t.co/yIUqYjqQnGFor the next major release we're dropping V2 support.     │               │            │
│            │                │ Their usability will rapidly diminish the next few months, as they're deprecated │               │            │
│            │                │ and @torproject will soon remove support. https://t.co/XEUbSnVmCe                │               │            │
├────────────┼────────────────┼──────────────────────────────────────────────────────────────────────────────────┼───────────────┼────────────┤
│ 2021-05-02 │ bitcoincoreorg │ Bitcoin Core 0.21.1 was released! It is available from https://t.co/WpMuMaejz1   │ 159           │ 583        │
│ 07:21:00   │                │ Release mail: https://t.co/TuFxSkQABE                                            │               │            │
├────────────┼────────────────┼──────────────────────────────────────────────────────────────────────────────────┼───────────────┼────────────┤
│ 2021-04-19 │ bitcoincoreorg │ Bitcoin Core 0.21.1 release candidate 1 available https://t.co/BSQjJiRuHw        │ 59            │ 222        │
│ 04:59:28   │                │ https://t.co/KQMiZFHnZy                                                          │               │            │
├────────────┼────────────────┼──────────────────────────────────────────────────────────────────────────────────┼───────────────┼────────────┤
│ 2021-01-19 │ achow101       │ I'm launching a Bitcoin Core usage survey: https://t.co/O3mbn4vnCPThe survey     │ 106           │ 0          │
│ 20:59:02   │                │ will help us learn about who, how, and why people use Bitcoin Core so that we    │               │            │
│            │                │ can improve it in the future. If you have any feedback about the software you    │               │            │
│            │                │ want to leave, this is the place to do it.                                       │               │            │
├────────────┼────────────────┼──────────────────────────────────────────────────────────────────────────────────┼───────────────┼────────────┤
│ 2021-01-14 │ bitcoincoreorg │ Bitcoin Core 0.21.0 was released It is available from https://t.co/jnWN8LRX75    │ 283           │ 907        │
│ 14:09:31   │                │ Release mail: https://t.co/6dFNUj3K4d                                            │               │            │
├────────────┼────────────────┼──────────────────────────────────────────────────────────────────────────────────┼───────────────┼────────────┤
│ 2020-08-01 │ bitcoincoreorg │ Bitcoin Core 0.20.1 was released It is available from https://t.co/Uy9NJ11mih    │ 216           │ 544        │
│ 13:15:33   │                │ (main website update pending) Release mail: https://t.co/95MXgRvN7Z              │               │            │
└────────────┴────────────────┴──────────────────────────────────────────────────────────────────────────────────┴───────────────┴────────────┘
```
