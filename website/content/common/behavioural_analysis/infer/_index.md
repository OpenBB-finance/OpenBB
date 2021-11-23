```
usage: infer [-n N_NUM] [-h]
```

Displays a quick sentiment inference from last tweets that contain the ticker. This model splits the text into character-level tokens and uses vader
sentiment analysis. Source: https://Twitter.com

```
optional arguments:
  -n N_NUM, --num N_NUM
                        num of latest tweets to infer from. (default: 100)
  -h, --help            show this help message (default: False)
```

<img width="1400" alt="Features Screenshot - infer" src="https://user-images.githubusercontent.com/25267873/128569570-7bec34ee-e024-4add-ab94-29df23af04ca.png">
