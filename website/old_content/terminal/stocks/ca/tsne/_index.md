```text
usage: tsne [-l LR] [-p] [-h]
```

Get similar companies to compare with using sklearn TSNE.

```
optional arguments:
  -r LR, --learnrate LR
                        TSNE Learning rate. Typical values are between 50 and 200 (default: 200)
  -l LIMIT, --limit LIMIT
                        Limit of stocks to retrieve. The subsample will occur randomly. (default: 10)
  -p, --no_plot
  -h, --help            show this help message (default: False)
```

![tsne](https://user-images.githubusercontent.com/46355364/154074416-af8c7d2a-fa2f-461f-8522-933cf6e3543b.png)
