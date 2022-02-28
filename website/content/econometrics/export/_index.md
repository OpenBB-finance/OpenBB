```
usage: export [-n NAME] [-t {csv,xlsx}] [-h]
```

Export dataset to Excel. It properly recognizes changes made with the `index`, `clean` and `modify` commands.

```
optional arguments:
  -n NAME, --name NAME  The name of the dataset you wish to export (default: None)
  -t {csv,xlsx}, --type {csv,xlsx}
                        The file type you wish to export to (default: xlsx)
  -h, --help            show this help message (default: False)
```

Example:
```
2022 Feb 24, 04:35 (✨) /econometrics/ $ load ThesisData.xlsx thesis

2022 Feb 24, 04:36 (✨) /econometrics/ $ export thesis -t csv
Saved file: /Users/jeroenbouma/My Drive/Programming/Python/GamestonkTerminal/exports/statistics/thesis_20220224_103614.csv
```
