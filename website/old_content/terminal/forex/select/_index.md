Select is separated in two options, "from" and "to":

```
usage: from [-n FROM_SYMBOL] [-h]
```

Select the "from" currency symbol in a forex pair

```
optional arguments:
  -n FROM_SYMBOL, --name FROM_SYMBOL
                        From currency (default: None)
  -h, --help            show this help message (default: False)
  ```

```
usage: to [-n TO_SYMBOL] [-h]
```

Select the "to" currency symbol in a forex pair

```
optional arguments:
  -n TO_SYMBOL, --name TO_SYMBOL
                        To currency (default: None)
  -h, --help            show this help message (default: False)
```

Example:

```
2022 Feb 15, 04:10 (🦋) /forex/ $ from USD

Selected pair
From: USD
To:   USD

2022 Feb 15, 04:10 (🦋) /forex/ $ to EUR

Selected pair
From: USD
To:   EUR
```
