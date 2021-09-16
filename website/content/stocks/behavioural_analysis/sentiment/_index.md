```
usage: sentiment [-n N_NUM] [-d N_DAYS_PAST]
```
Plot in-depth sentiment extracted from tweets from last days that contain pre-defined ticker. This model splits the text into character-level tokens and uses the VADER model to make predictions.
  * -n : num of tweets to extract per hour. Default 15.
  * -d : num of days in the past to extract tweets. Default 6. Max 6
