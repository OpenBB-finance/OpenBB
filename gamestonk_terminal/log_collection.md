# Log Collection Feature

## 1. Purpose

**GOAL**

In order to improve GamestonkTerminal, we need to know how people are using the tool, like :

- Which are the most used features
- Are they bugs/crashes on certain configuration (OS, python version...)

Knowing that we can focus part of our engineering effort on most common use cases.

**ISSUE**

GamestonkTerminal is an onsite application : that you install on your computer.

On a contrary of a web application that can track the usage of every button and page : we have no means to know what happens once GamestonkTerminal is installed on a computer.

**LOG COLLECTION**

Log Collection feature allow exportation of some GamestonkTerminal logs.

We are not logging credentials or elements that allows identifying you.

And we are exporting only limited portion of these logs.

## 2. How to setup : Log Collection ?

By default log collection are enabled.

**ENABLE**

Set this environment variable :

```sh
GTFF_LOG_COLLECTION = True
```

**DISABLE**

Set this environment variable :

```sh
GTFF_LOG_COLLECTION = False
```

## 3. What is collected ?

**PRIVACY**

We are making sure that none of this data are collect :

- data that let identify you
- credentials you might use with the Terminal

**DATA LIST**

Here is a list of data and whether they are collected or no :

|**Data**|**Description**|**Collected ?**|
|:-|:-|:-|
|User IP Address|User IP address.|NO|
|User API KEYS|API Keys to connect to third parties API, like : <br>- ALPHAVANTAGE <br> - COINBASE, <br>- COINPAPRIKA <br>- DEGIRO <br>- REDDIT|NO|
|User information|Other information that can let identify the users, like : <br>- E-mail <br> - LastName, <br>- Firstname|NO|
|Session duration|Start and end time of a session.|YES|
|Session size|Number of line logged within a user session.|YES|
|Number of error|Number of error lines logged within a user session.|YES|
|Commands|Commands run during a session, like : <br>- help <br>- load <br>- candle|NO|
|Commands arguments|Arguments of the commands run during a session, like : <br>- load TSLA|NO|
|Exception|Exception generated when a commands crashes : <br>- load TSLA|NO|
