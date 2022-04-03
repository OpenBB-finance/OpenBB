# DEGIRO

This menu aims to contain several commands that are available to a user through his Degiro account.

In order to be able to use these, just ensure you connect to your degiro account by typing `login` first.

## Credentials

In order to login you need to update [config file](/openbb_terminal/config_terminal.py) with the following credentials:

| Parameter | Description |
| :--- | :--- |
| DG_USERNAME | Username used to log into Degiro's website. |
| DG_PASSWORD | Password used to log into Degiro's website. |

## 2FA

In order to use 2FA you need to update [config file](/openbb_terminal/config_terminal.py) with:

| Parameter | Description |
| :--- | :--- |
| DG_TOTP_SECRET | This secret key will let Gamestonk generate the `OneTimePassword` for you. |

If you provide your `DG_TOTP_SECRET`, you won't have to type your `OneTimePassword`, Gamestonk will generate it for you
at each connection.

`DG_TOTP_SECRET` is the text representation of the `QRCODE` that Degiro's provide you when you enable 2FA.

More information on 2FA credentials, in the documentation of the [degiro-connector library](https://github.com/Chavithra/degiro-connector).

## Features

* [login](#login)
  * Connect to your Degiro account
* [logout](#login)
  * Disconnect from Degiro account

* [hold](#hold)
  * Command to look at current holdings
* [lookup](#lookup)
  * Command to search for a product by name

* [create](#create)
  * Create and `Order`
* [update](#update)
  * Update and `Order`
* [cancel](#cancel)
  * Cancel and `Order`
* [pending](#pending)
  * Command to list pending orders

* [companynews](#companynews)
  * Command to get news about a company with it's isin
* [lastnews](#lastnews)
  * Command to get latest news
* [topnews](#topnews)
  * Command to get top news preview

### login <a name="login"></a>

```text
usage: login [-u USERNAME] [-p PASSWORD] [-o OTP] [-s TOPT_SECRET] [-h]

optional arguments:
  -u USERNAME, --username USERNAME
                        Username in Degiro's account.
  -p PASSWORD, --password PASSWORD
                        Password in Degiro's account.
  -o OTP, --otp OTP     One time password (2FA).
  -s TOPT_SECRET, --topt-secret TOPT_SECRET
                        TOTP SECRET (2FA).
  -h, --help            show this help message
```

### logout <a name="logout"></a>

```text
usage: logout
```

### hold <a name="hold"></a>

```text
usage: hold
```

Displays current holdings to the console.

### lookup <a name="lookup"></a>

```text
usage: lookup TESLA
```

It will display a result like this :

```text
                           name          isin        symbol productType currency  closePrice closePriceDate
0                         Tesla  US88160R1014          TSLA       STOCK      USD     571.690     2021-05-13
1                     Tesla Inc  US88160R1014           TL0       STOCK      EUR     478.000     2021-05-13
2                     Tesla Inc  US88160R1014           TL0       STOCK      EUR     467.650     2021-05-13
3     TurboC O.End Tesla 535,04  DE000VQ1S3R3          None     WARRANT      EUR       3.740     2021-05-13
4      TurboC O.End Tesla 591,4  DE000VQ5R6T9          None     WARRANT      EUR       0.001     2021-05-13
5     TurboP O.End Tesla 685,29  DE000VQ7HWU6          None     WARRANT      EUR       9.870     2021-05-13
6     TurboC O.End Tesla 448,63  DE000VQ1KYG8          None     WARRANT      EUR      10.890     2021-05-13
7       Call 17.12.21 Tesla 392  DE000VP53547  DE000VP53547     WARRANT      EUR       8.960     2021-05-13
8       Call 20.01.23 Tesla 720  DE000VQ68691          None     WARRANT      EUR       1.160     2021-05-13
9  Leverage Shares 1x Tesla ETP  IE00BKT6ZH01          STSL         ETF      GBX     135.550     2021-05-13
```

### create <a name="create"></a>

```text
usage: create [-a {buy,sell}] (-prod PRODUCT | -sym SYMBOL) -p PRICE (-s SIZE | -up UP_TO) [-d {gtd,gtc}] [-t {limit,market,stop-limit,stop-loss}] [-h]
```

### update <a name="update"></a>

```text
usage: update ORDER_ID -p PRICE
```

### cancel <a name="cancel"></a>

```text
usage: cancel ORDER_ID
```

### pending <a name="pending"></a>

```text
usage: pending
```

### companynews <a name="companynews"></a>

```text
usage: companynews NL0000235190
```

You need to provide the `ISIN` number of the company.
You can get this `ISIN` using the `dglookup` command for instance.

### lastnews <a name="lastnews"></a>

```text
usage: lastnews [-l LIMIT] [-h]

optional arguments:
  -l LIMIT, --limit LIMIT
                        Number of news to display.
  -h, --help            show this help message
```

### topnews <a name="topnews"></a>

```text
usage: topnews
```
