# Log Collection Feature

## 1. Purpose

**CONTRIBUTE**

Code is not the only way you can contribute to improve GamestonkTerminal.

You can help the team by enabling sending the logs that contain information about the usage of the terminal and errors.

This helps to resolve bugs faster and focus the attention of the developers on what is important to you.

Together we can strengthen the open source community and channel our efforts.

This is important since GamestonkTerminal is an on-site application: you install it on your computer.

On a contrary of a web application that can track the usage of every button and page, we need logs to be sent to us to understand where to spend our time and effort.

With your logs, we can

- see what your favorite features are, understand why and further improve that part of the terminal
- have a look at the most common errors and improve on the ease of use
- we can check for incompatibilities of different operating systems and python versions

If you are concerned about privacy, be assured, we do not collect any Personal Identifiable Information (PII). This means that you will stay anonymous at all time.

Personal Identifiable Information : PII is anything that can link you to the data (IP/E-mail/Credentials...)

**LOG COLLECTION**

The Log Collection feature allows exportation of reports about GamestonkTerminal.

We are not logging credentials or elements that allows identifying you.

## 2. How to setup : Log Collection ?

By default Log Collection is enabled.

You can disable it running the command: `/settings/logcollection`

It should appear as red in the `/settings/help` table when disabled.

Run the same command another time to enable it.

It should appear as green in the `/settings/help` table when enabled.

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
|Python version|Python version on which GamestonkTerminal|<br>- 3.8.12 <br>- 3.9|YES|
|OS|Platform on which GamestonkTerminal, is running like|<br>- Linux <br>- Darwin <br>- Windows|YES|
|Exception/Error|When there is a crash of a command.||YES|
|Timestamp|Timestamp associated with logged information.|<br>- Launch <br>- Start of command<br>- End of command<br>- Exit<br>- Exception/Error|YES|
|Command|Commands and arguments run during a session|<br>- /help <br>- /crypto/disc/cpsearch -q eth <br>- /crypto/ov/cpinfo --help <br>- /stocks/load TSLA <br>- /stocks/candle --trend|YES|
