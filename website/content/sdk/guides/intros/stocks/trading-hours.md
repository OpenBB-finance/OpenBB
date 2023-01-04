---
title: Trading Hours
---

The Trading Hours sub-module is a set of functions for checking the status and hours of operation for markets globally.

## How to Use

There are only a handful of commands in the set, and they are listed below with a short description.

|Path |Description |
|:-----|----------:|
|openbb.stocks.th.open | Which Exchanges are Currently Open |
|openbb.stocks.th.all | All Exchanges and Their Status |
|openbb.stocks.th.exchange | Details for Individual Exchanges |
|openbb.stocks.th.closed | List of Closed Exchanges |

Alternatively, print the contents sub-module by entering:

```python
help(openbb.stocks.th)
```

## Examples

### All

Get a list of global exchanges and their current status.

```python
openbb.stocks.th.all()
```

|     | name                   | short_name   | open   |
|:----|:-----------------------|:-------------|:-------|
| SHZ | Shenzen Stock Exchange | SHZE         | False  |
| KSC | Korea Exchange         | KRX          | False  |
| KOE | Korea Exchange         | KRX          | False  |
| CAI | The Egyptian Exchange  | CA           | False  |
| PCX | NYSE Arca              | ARCA         | False  |
| SAT | Nasdaq OMX Stockholm   | ST           | False  |

### Open

See which exchanges are open right now.

```python
openbb.stocks.th.open()
```

|     | name                              | short_name   |
|:----|:----------------------------------|:-------------|
| CNQ | Canadian Securities Exchange: CSE | CN           |
| NZE | NZX                               | NZ           |
| MCX | MOEX                              | ME           |

### Exchange

Get the schedule of an individual exchange.

```python
openbb.stocks.th.exchange('CNQ')
```

|                       | CNQ                                                                                     |
|:----------------------|:----------------------------------------------------------------------------------------|
| name                  | Canadian Securities Exchange: CSE                                                       |
| short_name            | CN                                                                                      |
| website               | https://www.thecse.com/en/trading/trading-rules-and-links/trading-rules-and-regulations |
| market_open           | 08:00:00                                                                                |
| market_close          | 18:00:00                                                                                |
| lunchbreak_start      |                                                                                         |
| lunchbreak_end        |                                                                                         |
| opening_auction_start |                                                                                         |
| opening_auction_end   |                                                                                         |
| closing_auction_start |                                                                                         |
| closing_auction_end   |                                                                                         |
| timezone              | Canada/Eastern                                                                          |
| flag                  | 🇨🇦                                                                                      |
| open                  | True                                                                                    |
