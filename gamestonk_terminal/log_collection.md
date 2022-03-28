# Log Collection Feature

## 1. Purpose

**CONTRIBUTE**

Code is not the only way you can contribute to improve GamestonkTerminal.

You can help GamestonkTerminal Team by enabling reports about your usage and errors.

No Personal Identifiable Information is collected (PII).

Without this information we won't have much visibility on what are the :

- Most used features
- Most common errors
- OS + Python version : specific incompatibilities

Personal Identifiable Information : PII is anything that can link you to the data (IP/E-mail/Credentials...)

**CHALLENGE**

GamestonkTerminal is an on-site application : that you install on your computer.

On a contrary of a web application that can track the usage of every button and page.

We have no means to know if a feature we spent time and effort on is actually used or crashes.

**LOG COLLECTION**

The Log Collection feature allows exportation of reports about GamestonkTerminal.

We are not logging credentials or elements that allows identifying you.

## 2. How to setup : Log Collection ?

By default Log Collection is enabled.

You can disable it running the command : `/settings/logcollection`

It should appear as red in the `/settings/help` table when disabled.

Run the same command another time to enable it.

It should appear as green in the `/settings/help` table when enabled.

## 3. What is collected ?

**Personal Identifiable Information**

We everything we can to : filter any Personal Identifiable information and credentials.

Credentials are not logged at all.

**NOT COLLECTED**

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
