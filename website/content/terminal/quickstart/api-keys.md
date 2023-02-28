---
title: Obtain and Set API Keys for Data Providers
sidebar_position: 3
description: API (Application Programming Interface) keys are access credentials for accessing data from a particular source. They are a string of random characters assigned, by the data provider, to an individual account. Most vendors offer a free tier requiring only a valid email address. Each key is entered into the Terminal from the `/keys` menu, using the syntax described below. The `--help` dialogue for each source will also display the expected inputs.
keywords: [api, keys, api keys, data provider, data, free, alpha vantage, fred, iex, twitter, degiro, binance, coinglass, polygon, intrinio, openbb terminal]
---
## The Keys Menu

API (Application Programming Interface) keys are access credentials for obtaining data from a particular source. They are a string of random characters assigned, by the data provider, to an individual account. Most vendors offer a free tier requiring only a valid email address, some will require an account with proper KYC (Know Your Customer). Each source is entered into the Terminal from the `/keys` menu with the syntax as described in the sections below. Adding the `-h` argument to the command will also display the expected inputs. For example,

```console
/keys/reddit -h
```

Displays:

```console
usage: reddit [-i CLIENT_ID] [-s CLIENT_SECRET] [-u USERNAME] [-p PASSWORD] [-a USER_AGENT [USER_AGENT ...]] [-h]

Set Reddit API key.

options:
  -i CLIENT_ID, --id CLIENT_ID
                        Client ID (default: None)
  -s CLIENT_SECRET, --secret CLIENT_SECRET
                        Client Secret (default: None)
  -u USERNAME, --username USERNAME
                        Username (default: None)
  -p PASSWORD, --password PASSWORD
                        Password (default: None)
  -a USER_AGENT [USER_AGENT ...], --agent USER_AGENT [USER_AGENT ...]
                        User agent (default: None)
  -h, --help            show this help message (default: False)
```

A message similar to the one below will be printed when a function requesting data from an API is called but the key has not yet been entered.

```console
/stocks/fa/ $ rot

API_FINNHUB_KEY not defined. Set API Keys in ~/.openbb_terminal/.env or under keys menu.
```

The menu also provides a method for testing the validity of a key upon entry. It can be easy to copy & paste the string with a missing character; so, if the test fails, check that the values were correctly recorded with the command:

```console
mykeys --show
```

**We recommend gradually obtaining keys, when the use of a specific function requires it.**

## Summary List

<details>
<summary>Click to expand the list of data providers</summary>

| Command       | Name                                     | URL                                                                                |
| :------------ | :--------------------------------------- | :--------------------------------------------------------------------------------- |
| av            | AlphaVantage                             | https://www.alphavantage.co/support/#api-key                                       |
| binance       | Binance                                  | https://binance.com                                                                |
| bitquery      | Bitquery                                 | https://bitquery.io/                                                               |
| cmc           | CoinMarketCap                            | https://coinmarketcap.com/api/                                                     |
| coinbase      | Coinbase                                 | https://help.coinbase.com/en/exchange/managing-my-account/how-to-create-an-api-key |
| coinglass     | Coinglass                                | https://coinglass.github.io/API-Reference/#api-key                                 |
| cpanic        | Crypto Panic                             | https://cryptopanic.com/developers/api/                                            |
| degiro        | DeGiro                                   | https://www.degiro.com/                                                            |
| eodhd         | EODHD                                    | https://eodhistoricaldata.com/r/?ref=869U7F4J                                      |
| ethplorer     | Ethplorer                                | https://github.com/EverexIO/Ethplorer/wiki/Ethplorer-API                           |
| finnhub       | Finnhub                                  | https://finnhub.io/                                                                |
| fmp           | Financial Modelling Prep                 | https://site.financialmodelingprep.com/developer/docs/                             |
| fred          | Federal Reserve Economic Database (FRED) | https://fred.stlouisfed.org                                                        |
| github        | GitHub                                   | https://docs.github.com/en/rest/guides/getting-started-with-the-rest-api           |
| glassnode     | Glassnode                                | https://docs.glassnode.com/basic-api/api-key#how-to-get-an-api-key/                |
| iex           | IEX Cloud                                | https://iexcloud.io/                                                               |
| intrinio      | Intrinio                                 | https://intrinio.com/                                                              |
| messari       | Messari                                  | https://messari.io/api/docs                                                        |
| news          | News API                                 | https://newsapi.org/                                                               |
| oanda         | Oanda                                    | https://developer.oanda.com                                                        |
| polygon       | Polygon                                  | https://polygon.io                                                                 |
| quandl        | Quandl                                   | https://www.quandl.com                                                             |
| reddit        | Reddit                                   | https://www.reddit.com/wiki/api                                                    |
| rh            | Robinhood                                | https://robinhood.com/us/en/                                                       |
| santiment     | Santiment                                | https://app.santiment.net/                                                         |
| shroom        | ShroomDK                                 | https://sdk.flipsidecrypto.xyz/shroomdk                                            |
| smartstake    | Smartstake                               | https://www.smartstake.io                                                          |
| stocksera     | Stocksera                                | https://stocksera.pythonanywhere.com/                                              |
| tokenterminal | Token Terminal                           | https://tokenterminal.com/                                                         |
| tradier       | Tradier                                  | https://documentation.tradier.com/                                                 |
| twitter       | Twitter                                  | https://developer.twitter.com                                                      |
| walert        | Whale Alert                              | https://docs.whale-alert.io/                                                       |

</details>

## Instructions by Source

This section covers all API keys listed above and include detailed instructions how to obtain each API key. By clicking on each name, the section will expand and instructions are provided.

### AlphaVantage

<details>
<summary>Go to: https://www.alphavantage.co/support/#api-key</summary>

[AlphaVantage](https://www.alphavantage.co/support/#api-key)

![AlphaVantage](https://user-images.githubusercontent.com/46355364/207820936-46c2ba00-81ff-4cd3-98a4-4fa44412996f.png)

Fill out the form, pass Captcha, and click on, "GET FREE API KEY". The issued key can be entered into the OpenBB Terminal with:

```console
/keys/av REPLACE_WITH_KEY
```

</details>

### Binance

<details>
<summary>Go to: https://www.binance.com/en/support/faq/how-to-create-api-360002502072</summary>

[Binance](https://www.binance.com/en/support/faq/how-to-create-api-360002502072)

![Binance](https://user-images.githubusercontent.com/46355364/207839805-f71cf12a-62d2-41cb-ba19-0c35917abc40.png)

These instructions should provide clear guidance for obtaining an API Key. Enter the issued credentials into the OpenBB Terminal with:

```console
/keys/binance -k REPLACE_WITH_KEY -s REPLACE_WITH_SECRET
```

</details>

### Bitquery

<details>
<summary>Go to: https://bitquery.io/</summary>

[Bitquery](https://bitquery.io/)

![Bitquery](https://user-images.githubusercontent.com/46355364/207840322-5532a3f9-739f-4e28-9839-a58db932882e.png)

Click "Try GraphQL API", which opens the following screen:

![Try GraphQL API](https://user-images.githubusercontent.com/46355364/207840576-2c51a538-dd9b-484d-b11d-40e3e424df62.png)

After creating an account and verifying the email address, get the value for the key by clicking on the "API Key" tab.

![Get Bitquery API Key](https://user-images.githubusercontent.com/46355364/207840833-35c1b12c-9b4b-43fe-a33e-f7b92c43a011.png)

Enter this API key into the OpenBB Terminal by typing:

```console
/keys/bitquery REPLACE_WITH_KEY
```

</details>

### CoinMarketCap

<details>
<summary>Go to: https://coinmarketcap.com/api</summary>

[CoinMarketCap](https://coinmarketcap.com/api)

![CoinMarketCap](https://user-images.githubusercontent.com/46355364/207831111-3f09ed75-740e-4121-a67e-6e1f36e8ab9a.png)

Click on, "Get Your Free API Key Now", which opens to the page:

![CoinMarketCap](https://user-images.githubusercontent.com/46355364/207831345-06a48efe-63b2-4804-bcf9-52fa4a73f7db.png)

Once the account has been created, copy the API key displayed within the dashboard.

![CoinMarketCap](https://user-images.githubusercontent.com/46355364/207831705-e9f95018-bba7-49a9-b057-3443bc839861.png)

Enter the API key into the OpenBB Terminal by typing:

```console
/keys/cmc REPLACE_WITH_KEY
```

</details>

### Coinbase

<details>
<summary>Go to: https://help.coinbase.com/en/exchange/managing-my-account/how-to-create-an-api-key</summary>

[Coinbase](https://help.coinbase.com/en/exchange/managing-my-account/how-to-create-an-api-key)

![Coinbase](https://user-images.githubusercontent.com/46355364/207841901-647f0aef-0c74-454d-b99e-367d784259f0.png)

Follow the instructions to obtain the credentials for the specific account. Enter the three values into the OpenBB Terminal by typing:

```console
/keys/coinbase -k REPLACE_WITH_KEY -s REPLACE_WITH_SECRET -p REPLACE_WITH_PASSPHRASE
```

</details>

### Coinglass

<details>
<summary>Go to: https://www.coinglass.com/</summary>

[Coinglass](https://www.coinglass.com/)

![Coinglass](https://user-images.githubusercontent.com/46355364/207844601-8510687a-e54f-49b9-961f-5ef6718f58ab.png)

Click, "Log in", and then sign up for an account. This opens the page:

![Coinglass](https://user-images.githubusercontent.com/46355364/207844637-a9321889-c4d8-4d44-95fe-a6288a17ad19.png)

With the account created, find the assigned API key within the account profile page. Enter this value into the OpenBB Terminal by typing:

```console
/keys/coinglass REPLACE_WITH_KEY
```

</details>

### Crypto Panic

<details>
<summary>Go to: https://cryptopanic.com/developers/api/</summary>

[Crypto Panic](https://cryptopanic.com/developers/api/)

![Crypto Panic](https://user-images.githubusercontent.com/46355364/207848733-27e5a804-7ae7-4ca2-88b2-848b32929b6f.png)

Click on, [Sign up](https://cryptopanic.com/accounts/signup/?next=/developers/api/), and after creating, the API key will be displayed on the documentation page, "Your free API auth token".

![Crypto Panic](https://user-images.githubusercontent.com/46355364/207848971-3e4771b7-1faa-45fe-955f-81bd736b16b7.png)

Enter that value in the OpenBB Terminal by typing:

```console
/keys/cpanic REPLACE_WITH_KEY
```

</details>

### Databento

<details>
<summary>Go to: https://docs.databento.com/getting-started</summary>

[Databento](https://docs.databento.com/getting-started)

![Databento](databento.png)

Click on, [Sign up](databento2.png), and after creating an account, the API key is found in the [account portal](https://databento.com/portal/keys). Enter this into the terminal with:

```console
/keys/databento REPLACE_WITH_KEY
```

</details>

### Degiro

<details>
<summary>Go to: https://www.degiro.com/</summary>

[Degiro](https://www.degiro.com/)

![Degiro](https://user-images.githubusercontent.com/46355364/207838353-001d350c-872c-4770-a586-fb21318122eb.png)

Click on, "Open an account", and then go through the registration process. After setting up the account, the login credentials can be entered in the OpenBB Terminal with:

```console
/keys/degiro -u USERNAME -p PASSWORD 
```

Instructions for setting up 2FA authorization are [here](https://github.com/Chavithra/degiro-connector#35-how-to-use-2fa-).

</details>

### EODHD

<details>
<summary>Go to: https://eodhistoricaldata.com/r/?ref=869U7F4J</summary>

[EODHD](https://eodhistoricaldata.com/r/?ref=869U7F4J)

![EODHD](https://user-images.githubusercontent.com/46355364/207849214-23763c95-7314-42ae-b97d-cb5810686498.png)

Clicking on, "Registration", opens the page:

![EODHD](https://user-images.githubusercontent.com/46355364/207849324-00d4a916-8260-45c0-9714-289e0a0574c0.png)

Once registered, the API Key will be next to "API TOKEN".

![EODHD](https://user-images.githubusercontent.com/46355364/207849462-37471270-929a-45c5-a164-a84249b19231.png)

Enter this string into the OpenBB Terminal by typing:

```console
/keys/eodhd REPLACE_WITH_KEY
```

</details>

### Finnhub

<details>
<summary>Go to: https://finnhub.io/</summary>

[Finnhub](https://finnhub.io/)

![Finnhub](https://user-images.githubusercontent.com/46355364/207832028-283c3321-8c05-4ee8-b4d2-41cdc940f408.png)

Click on, "Get free api key", to open the page:

![Finnhub](https://user-images.githubusercontent.com/46355364/207832185-f4c8406a-3b75-4acc-b3e8-3c4b3272d4da.png)

Once the account has been created, find the API key in the account dashboard.

![Finnhub](https://user-images.githubusercontent.com/46355364/207832601-62007d95-410c-4d03-a5a3-b177d1894a4c.png)

Add this key to the OpenBB Terminal by entering:

```console
/keys/finnhub REPLACE_WITH_KEY
```

</details>

### Financial Modeling Prep

<details>
<summary>Go to: https://site.financialmodelingprep.com/developer/docs</summary>

[FinancialModelingPrep](https://site.financialmodelingprep.com/developer/docs)

![FinancialModelingPrep](https://user-images.githubusercontent.com/46355364/207821920-64553d05-d461-4984-b0fe-be0368c71186.png)

Click on, "Get my API KEY here", and sign up for a free account.

![FinancialModelingPrep](https://user-images.githubusercontent.com/46355364/207822184-a723092e-ef42-4f87-8c55-db150f09741b.png)

With an account created, sign in and navigate to the Dashboard, which shows the assigned token. by pressing the "Dashboard" button which will show the API key.

![FinancialModelingPrep](https://user-images.githubusercontent.com/46355364/207823170-dd8191db-e125-44e5-b4f3-2df0e115c91d.png)

Enter the key into the OpenBB Terminal with:

```console
/keys/fmp REPLACE_WITH_KEY
```

</details>

### FRED

<details>
<summary>Go to: https://fred.stlouisfed.org</summary>

[FRED](https://fred.stlouisfed.org)

![FRED](https://user-images.githubusercontent.com/46355364/207827137-d143ba4c-72cb-467d-a7f4-5cc27c597aec.png)

Click on, "My Account", create a new account or sign in with Google:

![FRED](https://user-images.githubusercontent.com/46355364/207827011-65cdd501-27e3-436f-bd9d-b0d8381d46a7.png)

After completing the sign-up, go to "My Account", and select "API Keys". Then, click on, "Request API Key".

![FRED](https://user-images.githubusercontent.com/46355364/207827577-c869f989-4ef4-4949-ab57-6f3931f2ae9d.png)

Fill in the box for information about the use-case for FRED, and by clicking, "Request API key", at the bottom of the page, the API key will be issued.

![FRED](https://user-images.githubusercontent.com/46355364/207828032-0a32d3b8-1378-4db2-9064-aa1eb2111632.png)

Enter the API key into the OpenBB Terminal with:

```console
/keys/fred REPLACE_WITH_KEY
```

</details>

### GitHub

<details>
<summary>Go to: https://github.com</summary>

[GitHub](https://github.com)

![GitHub](https://user-images.githubusercontent.com/46355364/207846953-7feae777-3c3b-4f21-9dcf-84817c732618.png)

Sign up for, or sign in to, GitHub. Once logged in, navigate to the [apps](https://github.com/settings/apps) page, under account settings.

![GitHub](https://user-images.githubusercontent.com/46355364/207847215-3c04003f-26ea-4e62-9c13-ea35176bb5e3.png)

Select, "New GitHub App":

![GitHub](https://user-images.githubusercontent.com/46355364/207847383-d24416c6-18be-43f2-ae7c-455e8372a6ed.png)

After creating the app, the key will be issued. Enter this token into the OpenBB Terminal with:

```console
/keys/github REPLACE_WITH_KEY
```

</details>

### Glassnode

<details>
<summary>Go to: https://studio.glassnode.com</summary>

[Glassnode](https://studio.glassnode.com)

![Glassnode](https://user-images.githubusercontent.com/46355364/207843761-799078ff-fa64-4d39-a6eb-ba01d250be69.png)

Click on, "Sign up", and create an account:

![Glassnode](https://user-images.githubusercontent.com/46355364/207843795-dd2cdbdb-45eb-4c7d-b967-ae9857d4ea5d.png)

After creating an account, navigate to the [account settings](https://studio.glassnode.com/settings/api) and generate an API Key.

![Glassnode](https://user-images.githubusercontent.com/46355364/207843950-5f33f37d-0203-4302-a67f-198808f18e06.png)

Enter this key in the OpenBB terminal with:

```console
/keys/glassnode REPLACE_WITH_KEY
```

</details>

### IEX Cloud

<details>
<summary>Go to: https://iexcloud.io</summary>

[IEX Cloud](https://iexcloud.io)

![IEX Cloud](https://user-images.githubusercontent.com/46355364/207833088-e879e9f2-3180-4e50-ba9e-f40ee958f98a.png)

Click on, "Sign in", and then create a new account.

![IEX Cloud](https://user-images.githubusercontent.com/46355364/207833011-542d6ef0-0bdf-494a-83cb-c0a6741df2a3.png)

After signing up, select a plan. There is a choice for a free plan at the bottom.

![IEX Cloud](https://user-images.githubusercontent.com/46355364/207833303-4ebb2880-0b4c-4008-9b33-0e8ee6836027.png)

After completing the sign-up process, the API Keyis found under the, "Access & Security", tab.

![IEX Cloud](https://user-images.githubusercontent.com/46355364/207833540-c1e25500-22e9-43c3-a89e-b05dd446f2a5.png)

Add this API key to the OpenBB Terminal by entering:

```console
/keys/iex REPLACE_WITH_KEY
```

</details>

### Intrinio

<details>
<summary>Go to: https://intrinio.com/starter-plan</summary>

[Intrinio](https://intrinio.com/starter-plan)

![Intrinio](https://user-images.githubusercontent.com/85772166/219207556-fcfee614-59f1-46ae-bff4-c63dd2f6991d.png)

An API key will be issued with a subscription. Find the token value within the account dashboard, and enter it into the OpenBB Terminal with:

```console
/keys/intrinio REPLACE_WITH_KEY
```

</details>

### Messari

<details>
<summary>Go to: https://messari.io</summary>

[Messari](https://messari.io)

![Messari](https://user-images.githubusercontent.com/46355364/207848122-ec6a41e4-76b7-4620-adc3-1f1c19f4bca6.png)

Click on, "Sign up", and create an account.

![Messari](https://user-images.githubusercontent.com/46355364/207848160-6a962e3c-3007-40a3-9431-cd5ddfe5bb8e.png)

After creating the account, navigate to the [account page](https://messari.io/account/api), and click on the tab for, API Access.

![Messari](https://user-images.githubusercontent.com/46355364/207848324-ade5bede-8e6b-4b87-bdec-eade3217c0d8.png)

Copy the API key and add it to the OpenBB Terminal by entering:

```console
/keys/messari REPLACE_WITH_KEY
```

</details>

### News API

<details>
<summary>Go to: https://newsapi.org</summary>

[News API](https://newsapi.org)

![News API](https://user-images.githubusercontent.com/46355364/207828250-0c5bc38c-90b4-427d-a611-b43c98c8e7ab.png)

Click on, "Get API Key", and fill out the form.

![News API](https://user-images.githubusercontent.com/46355364/207828421-76922bc2-cde0-493f-9eed-7f90eb831779.png)

Register for an account and the next screen will provide the API Key.

![News API](https://user-images.githubusercontent.com/46355364/207828736-f0fce53b-f302-4456-adf9-8d50ac41fbe2.png)

Add this API key into the OpenBB Terminal by entering:

```console
/keys/news REPLACE_WITH_KEY
```

</details>

### Oanda

<details>
<summary>Go to: https://developer.oanda.com</summary>

[Oanda](https://developer.oanda.com)

![Oanda](https://user-images.githubusercontent.com/46355364/207839324-d30aa2b6-be83-41ff-9b1b-146cac566789.png)

After creating an account, follow the steps below.

![Oanda](https://user-images.githubusercontent.com/46355364/207839246-eb40f093-b583-4edd-b178-99fe399bfb66.png)

Upon completion of the account setup, enter the credentials into the OpenBB Terminal using the syntax:

```console
/keys/oanda -a REPLACE_WITH_ACCOUNT -t REPLACE_WITH_TOKEN --account_type REPLACE_WITH_LIVE_OR_PRACTICE
```

</details>

### Polygon

<details>
<summary>Go to: https://polygon.io</summary>

[Polygon](https://polygon.io)

![Polygon](https://user-images.githubusercontent.com/46355364/207825623-fcd7f0a3-131a-4294-808c-754c13e38e2a.png)

Click on, "Get your Free API Key".

![Polygon](https://user-images.githubusercontent.com/46355364/207825952-ca5540ec-6ed2-4cef-a0ed-bb50b813932c.png)

After signing up, the API Key is found at the bottom of the account dashboard page.

![Polygon](https://user-images.githubusercontent.com/46355364/207826258-b1f318fa-fd9c-41d9-bf5c-fe16722e6601.png)

Enter the key into the OpenBB Terminal by typing:

```console
/keys/polygon REPLACE_WITH_KEY
```

</details>

### Quandl

<details>
<summary>Go to: https://www.quandl.com</summary>

[Quandl](https://www.quandl.com)

![Quandl](https://user-images.githubusercontent.com/46355364/207823899-208a3952-f557-4b73-aee6-64ac00faedb7.png)

Click on, "Sign Up", and register a new account.

![Quandl](https://user-images.githubusercontent.com/46355364/207824214-4b6b2b74-e709-4ed4-adf2-14803e6f3568.png)

Follow the sign-up instructions, and upon completion the API key will be assigned.

![Quandl](https://user-images.githubusercontent.com/46355364/207824664-3c82befb-9c69-42df-8a82-510d85c19a97.png)

Enter the key into the OpenBB Terminal with:

```console
/keys/quandl REPLACE_WITH_KEY
```

</details>

### Reddit

<details>
<summary>Sign in to Reddit, and then go to: https://old.reddit.com/prefs/apps/</summary>

[Reddit](https://old.reddit.com/prefs/apps/)

![Reddit](https://preview.redd.it/540vrn3k0cn91.png?width=986&format=png&auto=webp&v=enabled&s=88228cd0cf4415b3487b8d35e1097f0caa804e15)

Scroll down and click on "create application", selecting "script".

![Reddit](https://preview.redd.it/7je4ehqa1cn91.png?width=916&format=png&auto=webp&v=enabled&s=dbdf65ccc0820cfe28eff8e81cba056f4fd8263e)

Once the application is created, you must register it [here](https://old.reddit.com/wiki/api)

![Reddit](https://user-images.githubusercontent.com/46355364/207834105-665180be-c2b6-43c8-b1c9-477729905010.png)

Click on, "Read the full API terms and sign up for usage", and fill out the form.

![Reddit](https://user-images.githubusercontent.com/46355364/207834850-32a0d4c8-9990-4919-94e3-abad1487a3bd.png)

After submitting the form, check for a confirmation email. The credentials will be displayed [here](https://old.reddit.com/prefs/apps/), enter them into the OpenBB Terminal in one line:

```console
/keys/reddit -i REPLACE_WITH_CLIENT_ID -s REPLACE_WITH_CLIENT_SECRET -u REPLACE_WITH_REDDIT_USERNAME -p REPLACE_WITH_REDDIT_PASSWORD -a REPLACE_WITH_USER_AGENT
```

</details>

### Robinhood

<details>
<summary>Go to: https://robinhood.com/us/en</summary>

[Robinhood](https://robinhood.com/us/en)

![Robinhood](https://user-images.githubusercontent.com/46355364/207838058-a2311632-6459-4cfd-bc0a-639ee3931574.png)

After registering for an account, it can be added to the OpenBB Terminal with:

```console
/keys/rb -u REPLACE_WITH_USERNAME -p REPLACE_WITH_PASSWORD
```

The first login will request 2FA authorization from the device connected to the account.

</details>

### Santiment

<details>
<summary>Go to: https://app.santiment.net</summary>

![Santiment](https://user-images.githubusercontent.com/46355364/207849709-a5f10b03-138c-4e09-89f6-8a18cfbaf008.png)

Click on, "Sign up", and register for an account.

![Santiment](https://user-images.githubusercontent.com/46355364/207849732-4bae61de-2f62-4919-b85d-f418f1bbd0c4.png)

Navigate to the [account dashboard](https://app.santiment.net/account#api-keys) and generate a key.

![Santiment](https://user-images.githubusercontent.com/46355364/207849839-31d1d0a7-6936-4ebd-a7f8-1292f6317b07.png)

Add it to the OpenBB Terminal by entering:

```console
/keys/santiment REPLACE_WITH_KEY
```

</details>

### ShroomDK

<details>
<summary>Go to: https://sdk.flipsidecrypto.xyz/shroomdk</summary>

[ShroomDK](https://sdk.flipsidecrypto.xyz/shroomdk)

![ShroomDK](https://user-images.githubusercontent.com/46355364/207850122-b8cd225e-0a65-4ea8-8069-0b40fff1600e.png)

Click "Mint Your ShroomDK API Key", and sign up for an account.

![ShroomDK](https://user-images.githubusercontent.com/46355364/207850176-f29cc73b-2b55-46e8-bce3-62c9342b6599.png)

Once created, connect a wallet to complete minting the NFT license. The API key will be displayed under the account.

![ShroomDK](https://user-images.githubusercontent.com/46355364/207850380-b59554af-1e65-4616-921d-e02c9ecf1aad.png)

Enter it into the OpenBB Terminal by typing:

```console
/keys/shroom REPLACE_WITH_KEY
```

</details>

### Stocksera

<details>
<summary>Go to: https://stocksera.pythonanywhere.com</summary>

[Stocksera](https://stocksera.pythonanywhere.com)

![Stocksera](https://user-images.githubusercontent.com/46355364/207853896-ee233569-26bb-4244-b115-43ac8885757a.png)

Click on, "Log in", and create an account.

![Stocksera](https://user-images.githubusercontent.com/46355364/207853985-46a7a17f-b6b2-442b-886d-f68b3ba2ad5a.png)

Once logged in, navigate to the "Developers" tab and copy the API key.

![Stocksera](https://user-images.githubusercontent.com/46355364/207854224-e5ddace0-15d1-491c-b616-263cca0bef02.png)

Add the key to the OpenBB Terminal by entering:

```console
/keys/stocksera REPLACE_WITH_KEY
```

</details>

### Token Terminal

<details>
<summary>Go to: https://tokenterminal.com</summary>

[Token Terminal](https://tokenterminal.com)

![Token Terminal](https://user-images.githubusercontent.com/46355364/207850735-69368b4f-6a3e-46b8-ba69-3b79d9231f15.png)

Click on, "Log in" and sign up for an account.

![Token Terminal](https://user-images.githubusercontent.com/46355364/207850774-2071df78-3289-4c8e-9d64-156b9ec8ad81.png)

Verify the email address, and then navigate go to the "API" tab and copy the API key to the clipboard.

![Token Terminal](https://user-images.githubusercontent.com/46355364/207851035-71ea3eff-a11f-4835-8592-c07b3aa3f800.png)

Add the key to the OpenBB Terminal by typing:

```console
/keys/tokenterminal REPLACE_WITH_KEY
```

</details>

### Tradier

<details>
<summary>Go to: https://documentation.tradier.com</summary>

[Tradier](https://documentation.tradier.com)

![Tradier](https://user-images.githubusercontent.com/46355364/207829178-a8bba770-f2ea-4480-b28e-efd81cf30980.png)

Click on, "Open Account", to start the sign-up process. After the account has been setup, navigate to [Tradier Broker Dash](https://dash.tradier.com/login?redirect=settings.api) and create the application. Request a sandbox access token, and enter this key into the OpenBB Terminal with:

```console
/keys/tradier REPLACE_WITH_KEY
```

</details>

### Twitter

<details>
<summary>Upcoming changes to the Twitter API will deprecate the current functionality, it is uncertain if the current features will continue to work. </summary>

![Twitter API](https://pbs.twimg.com/media/FooIJF3agAIU8SN?format=png&name=medium)

</details>

### Whale Alert

<details>
<summary>Go to: https://docs.whale-alert.io</summary>

[Whale Alert](https://docs.whale-alert.io)

![Whale Alert](https://user-images.githubusercontent.com/46355364/207842892-3f71ee7a-6cd3-48a2-82e4-fa5ec5b13807.png)

Click on, "sign up here".

![Whale Alert](https://user-images.githubusercontent.com/46355364/207842992-427f1d2c-b34e-41c9-85fd-18511805fd16.png)

After creating the account, click on, "Create", to issue the API Key.

![Whale Alert](https://user-images.githubusercontent.com/46355364/207843214-20232465-9a52-4b66-b01a-0b8cecbdd612.png)

Enter the key into the OpenBB Terminal by typing:

```console
/keys/walert REPLACE_WITH_KEY
```

</details>
