# `Reporting`

This document explains `GamestonkTerminal` `Reporting` feature.

## 1. Purpose

**CONTRIBUTE**

Code is not the only way you can contribute to improve `GamestonkTerminal`.

You can help the `GamestonkTerminal` Community by enabling sending logs about the usage of the terminal and errors.

We are not logging credentials or elements that allows identifying you.


**REASONS**

Together we can strengthen the open source community and channel our efforts.

This helps to resolve bugs faster and focus the attention of the developers on what is important to you.

This is important since `GamestonkTerminal` is an on-site application: you install it on your computer.

On a contrary of a web application that can track the usage of every button and page, we need logs to be sent to us to understand where to spend our time and effort.

With your this reports, we can :
1. see what your favorite features are, understand why and further improve that part of the terminal
2. have a look at the most common errors and improve on the ease of use
3. we can check for incompatibilities of different operating systems and python versions

If you are concerned about privacy, be assured, we do not collect any Personal Identifiable Information (PII).

This means that you will stay anonymous at all time.

## 2. Disable/Enable `Reporting` ?

By default Reporting is enabled.

You can disable it running the command: `/settings/logcollection`

The key `logcollection` should appear in red in the `/settings/help` table when disabled.

You can do the same operation to re-enable it : `logcollection` will appear in green.

## 3. What is and is not collected ?

**NOT COLLECTED**

*Personal Identifiable Information*

We have a filter in place, to prevent any Personal Identifiable information and credentials to be saved in the logs.

Credentials are not logged at all.

Here is a list of data we are not collecting :

|**Data**|**Description**|**Collected ?**|
|:-|:-|:-|
|User IP Address|User IP address.|NO|
|User API KEYS|API Keys to connect to third parties API, like : <br>- ALPHAVANTAGE <br> - COINBASE, <br>- COINPAPRIKA <br>- DEGIRO <br>- REDDIT|NO|
|User information|Other information that can let identify the users, like : <br>- E-mail <br> - LastName <br>- Firstname|NO|
|File/Folder paths|When errors occurs usually computers paths are shown : we filter those.|NO|

**COLLECTED**

Here is an exhaustive list of what can be collected :

|**Data**|**Description**|**Examples**|**Collected ?**|
|:-|:-|:-|:-|
|Python version|Python version on which `GamestonkTerminal`|<br>- 3.8.12 <br>- 3.9|YES|
|OS|Platform on which `GamestonkTerminal`, is running like|<br>- Linux <br>- Darwin <br>- Windows|YES|
|Exception/Error|When there is a crash of a command.||YES|
|Timestamp|Timestamp associated with logged information.|<br>- Launch <br>- Start of command<br>- End of command<br>- Exit<br>- Exception/Error|YES|
|Command|Commands and arguments run during a session|<br>- /help <br>- /crypto/disc/cpsearch -q eth <br>- /crypto/ov/cpinfo --help <br>- /stocks/load TSLA <br>- /stocks/candle --trend|YES|
