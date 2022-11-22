```
usage: rmv [-k RMV_STRIKE] [-h]
```

Remove one or all of the options from the diagram.

```
optional arguments:
  -i RMV_STRIKE, --index RMV_STRIKE
                        index of the option to remove
  -a, --all             remove all of the options
  -h, --help            show this help message
```

Example:

```
2022 Feb 16, 09:28 (🦋) /stocks/options/payoff/ $ rmv 0
#       Type    Hold    Strike  Cost
0       call    Long    780.0   141.96
1       call    Long    850.0   102.0
2       call    Long    875.0   89.4
3       call    Long    600.0   320.73
4       call    Long    700.0   226.06

2022 Feb 16, 09:28 (🦋) /stocks/options/payoff/ $ rmv 3
#       Type    Hold    Strike  Cost
0       call    Long    780.0   141.96
1       call    Long    850.0   102.0
2       call    Long    875.0   89.4
3       call    Long    700.0   226.06

2022 Feb 16, 09:28 (🦋) /stocks/options/payoff/ $ rmv 2
#       Type    Hold    Strike  Cost
0       call    Long    780.0   141.96
1       call    Long    850.0   102.0
2       call    Long    700.0   226.06
```
