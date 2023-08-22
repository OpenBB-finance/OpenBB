---
title: Setting API Keys
sidebar_position: 1
description: API (Application Programming Interface) keys are access credentials for accessing data from a particular source. Learn how to set, manage, and access data APIs for the OpenBB SDK.
keywords: [api, keys, api keys, data provider, data, free, alpha vantage, fred, iex, twitter, degiro, binance, coinglass, polygon, intrinio, sdk, alphavantage, bitquery, coinbase, databento, finnhub, FRED, github, glassnode, iex cloud, news API, robinhood, santiment, shroomdk, token terminal, tradier, twitter, whale alert]
---

import HeadTitle from '@site/src/components/General/HeadTitle.tsx';

<HeadTitle title="API Keys - SDK | OpenBB Docs" />

## The Keys Module

API (Application Programming Interface) keys are access credentials for obtaining data from a particular source. They are a string of random characters assigned, by the data provider, to an individual account. Most vendors offer a free tier requiring only a valid email address, some will require an account with proper KYC (Know Your Customer). Each source is entered into the SDK with the `openbb.keys` module, using the syntax described in the sections below. Wrapping the command with `help()` will print the docstrings to the screen. For example:

```console
help(openbb.keys.reddit)
```

Which prints:

```console
    Set Reddit key

    Parameters
    ----------
    client_id: str
        Client ID
    client_secret: str
        Client secret
    password: str
        User password
    username: str
        User username
    useragent: str
        User useragent
    persist: bool, optional
        If False, api key change will be contained to where it was changed. For example, a Jupyter notebook session.
        If True, api key change will be global, i.e. it will affect terminal environment variables.
        By default, False.
    show_output: bool, optional

    Returns
    -------
    str
        Status of key set

    Examples
    --------
    >>> from openbb_terminal.sdk import openbb
    >>> openbb.keys.reddit(
            client_id="example_id",
            client_secret="example_secret",
            password="example_password",
            username="example_username",
            useragent="example_useragent"
        )
```

A message similar to the one below will be printed when a function requesting data from an API is called but the key has not yet been entered.

```console
openbb.stocks.quote("AAPL")
API_KEY_FINANCIALMODELINGPREP not defined. Set API Keys in ~/.openbb_terminal/.env or under keys menu.
```

The menu also provides a method for testing the validity of a key upon entry. It can be easy to copy & paste the string with a missing character; so, if the test fails, check that the values were correctly recorded with the command:

```console
openbb.keys.mykeys(show = True)
```

**We recommend gradually obtaining keys, when the use of a specific function requires it.**

## Instructions by Source

This section covers all API keys listed above and include detailed instructions how to obtain each API key. By clicking on each name, the section will expand and instructions are provided. Include, `persist = True` in the syntax to permanently store the key on the machine.

### AlphaVantage

> Alpha Vantage provides enterprise-grade financial market data through a set of powerful and developer-friendly data APIs and spreadsheets. From traditional asset classes (e.g., stocks, ETFs, mutual funds) to economic indicators, from foreign exchange rates to commodities, from fundamental data to technical indicators, Alpha Vantage is your one-stop-shop for real-time and historical global market data delivered through cloud-based APIs, Excel, and Google Sheets.

<details>
<summary>Instructions</summary>

Go to: https://www.alphavantage.co/support/#api-key

[AlphaVantage](https://www.alphavantage.co/support/#api-key)

![AlphaVantage](https://user-images.githubusercontent.com/46355364/207820936-46c2ba00-81ff-4cd3-98a4-4fa44412996f.png)

Fill out the form, pass Captcha, and click on, "GET FREE API KEY". The issued key can be entered into the OpenBB SDK with:

```console
openbb.keys.av(key = 'REPLACE_WITH_KEY', persist = True)
```

</details>

### Binance

> Binance cryptocurrency exchange - We operate the worlds biggest bitcoin exchange and altcoin crypto exchange in the world by volume

<details>
<summary>Instructions</summary>

Go to: https://www.binance.com/en/support/faq/how-to-create-api-360002502072

![Binance](https://user-images.githubusercontent.com/46355364/207839805-f71cf12a-62d2-41cb-ba19-0c35917abc40.png)

These instructions should provide clear guidance for obtaining an API Key. Enter the issued credentials into the OpenBB SDK with:

```console
openbb.keys.binance(
    key = 'REPLACE_WITH_KEY',
    secret = 'REPLACE_WITH_SECRET',
    persist = True
)
```

</details>

### Bitquery

> Bitquery is an API-first product company dedicated to power and solve blockchain data problems using the ground truth of on-chain data.

<details>
<summary>Instructions</summary>

Go to: https://bitquery.io/<

![Bitquery](https://user-images.githubusercontent.com/46355364/207840322-5532a3f9-739f-4e28-9839-a58db932882e.png)

Click "Try GraphQL API", which opens the following screen:

![Try GraphQL API](https://user-images.githubusercontent.com/46355364/207840576-2c51a538-dd9b-484d-b11d-40e3e424df62.png)

After creating an account and verifying the email address, get the value for the key by clicking on the "API Key" tab.

![Get Bitquery API Key](https://user-images.githubusercontent.com/46355364/207840833-35c1b12c-9b4b-43fe-a33e-f7b92c43a011.png)

Enter this API key into the OpenBB SDK with:

```console
openbb.keys.bitquery(key = 'REPLACE_WITH_KEY', persist = True)
```

</details>

### BizToc

> BizToc is the one-stop business and finance news hub, encapsulating the top 200 US news providers in real time.

<details>
<summary>Instructions</summary>

The BizToc API is hosted on RapidAPI.  To set up, go to: https://rapidapi.com/thma/api/biztoc.

![biztoc0](https://github.com/marban/OpenBBTerminal/assets/18151143/04cdd423-f65e-4ad8-ad5a-4a59b0f5ddda)

In the top right, select "Sign Up".  After answering some questions, you will be prompted to select one of their plans.

![biztoc1](https://github.com/marban/OpenBBTerminal/assets/18151143/9f3b72ea-ded7-48c5-aa33-bec5c0de8422)

After signing up, navigate back to https://rapidapi.com/thma/api/biztoc.  If you are logged in, you will see a header called X-RapidAPI-Key.

![biztoc2](https://github.com/marban/OpenBBTerminal/assets/18151143/0f3b6c91-07e0-447a-90cd-a9e23522929f)

Copy the key to the clipboard, and enter this key into the OpenBB Terminal with:

```console
openbb.keys.biztoc(key = "REPLACE_WITH_KEY", persist=True)
```

</details>

### CoinMarketCap

### CoinMarketCap

> CoinMarketCap is the world's most-referenced price-tracking website for cryptoassets in the rapidly growing cryptocurrency space. Its mission is to make crypto discoverable and efficient globally by empowering retail users with unbiased, high quality and accurate information for drawing their own informed conclusions.

<details>
<summary>Instructions</summary>

Go to: https://coinmarketcap.com/api

![CoinMarketCap](https://user-images.githubusercontent.com/46355364/207831111-3f09ed75-740e-4121-a67e-6e1f36e8ab9a.png)

Click on, "Get Your Free API Key Now", which opens to the page:

![CoinMarketCap](https://user-images.githubusercontent.com/46355364/207831345-06a48efe-63b2-4804-bcf9-52fa4a73f7db.png)

Once the account has been created, copy the API key displayed within the dashboard.

![CoinMarketCap](https://user-images.githubusercontent.com/46355364/207831705-e9f95018-bba7-49a9-b057-3443bc839861.png)

Enter the API key into the OpenBB SDK with:

```console
openbb.keys.cmc(key = 'REPLACE_WITH_KEY', persist = True)
```

</details>

### Coinbase

> Coinbase is a secure online platform for buying, selling, transferring, and storing cryptocurrency.

<details>
<summary>Instructions</summary>

Go to: https://help.coinbase.com/en/exchange/managing-my-account/how-to-create-an-api-key

![Coinbase](https://user-images.githubusercontent.com/46355364/207841901-647f0aef-0c74-454d-b99e-367d784259f0.png)

Follow the instructions to obtain the credentials for the specific account. Enter the three values into the OpenBB SDK with:

```console
openbb.keys.coinbase(
    key = 'REPLACE_WITH_KEY',
    secret = 'REPLACE_WITH_SECRET',
    passphrase = 'REPLACE_WITH_PASSPHRASE',
    persist = True
)
```

</details>

### Coinglass

> Coinglass is a cryptocurrency futures trading & information platform,where you can find the Bitcoin Liquidations ,Bitcoin open interest, Grayscale Bitcoin Trust，Bitcoin longs vs shorts ratio and actively compare funding rates for crypto futures.Above all the quantities are shown as per their respective contract value.

<details>
<summary>Instructions</summary>

Go to: https://www.coinglass.com/

![Coinglass](https://user-images.githubusercontent.com/46355364/207844601-8510687a-e54f-49b9-961f-5ef6718f58ab.png)

Click, "Log in", and then sign up for an account. This opens the page:

![Coinglass](https://user-images.githubusercontent.com/46355364/207844637-a9321889-c4d8-4d44-95fe-a6288a17ad19.png)

With the account created, find the assigned API key within the account profile page. Enter this value into the OpenBB SDK with:

```console
openbb.keys.coinglass(key = 'REPLACE_WITH_KEY', persist = True)
```

</details>

### Crypto Panic

> CryptoPanic is a news aggregator platform indicating impact on price and market for traders and cryptocurrency enthusiasts.

<details>
<summary>Instructions</summary>

Go to: https://cryptopanic.com/developers/api/

![Crypto Panic](https://user-images.githubusercontent.com/46355364/207848733-27e5a804-7ae7-4ca2-88b2-848b32929b6f.png)

Click on, [&#34;Sign up&#34;](https://cryptopanic.com/accounts/signup/?next=/developers/api/), and after creating, the API Key will be displayed on the documentation page, "Your free API auth token".

![Crypto Panic](https://user-images.githubusercontent.com/46355364/207848971-3e4771b7-1faa-45fe-955f-81bd736b16b7.png)

Enter that value in the OpenBB SDK with:

```console
openbb.keys.cpanic(key = 'REPLACE_WITH_KEY', persist = True)
```

</details>

### Databento

> Databento eliminates tens of thousands of dollars in upfront expenses per dataset without sacrificing data integrity. We give you the flexibility to pick up real-time full exchange feeds and terabytes of historical data, whenever you need it.

<details>
<summary>Instructions</summary>

Go to: https://docs.databento.com/getting-started

![Databento](https://user-images.githubusercontent.com/85772166/221944000-394e7123-5bb3-4218-b949-f0958b6353da.png)

Click on, [Sign up](https://databento.com/signup), and after creating an account, the API key is found in the [account portal](https://databento.com/portal/keys).

![Databento](https://user-images.githubusercontent.com/85772166/221944057-c2314909-7b7d-4f65-8e9e-287a957f54f8.png)

Enter this into the terminal with:

```console
openbb.keys.databento(key = 'REPLACE_WITH_KEY')
```

</details>

### Degiro

> DEGIRO is Europe's fastest growing online stock broker. DEGIRO distinguishes itself from its competitors by offering extremely low trading commissions.

<details>
<summary>Instructions</summary>

Go to: https://www.degiro.com/

![Degiro](https://user-images.githubusercontent.com/46355364/207838353-001d350c-872c-4770-a586-fb21318122eb.png)

Click on, "Open an account", and then go through the registration process. After setting up the account, the login credentials can be entered in the OpenBB SDK with:

```console
openbb.keys.degiro(
    username = 'USERNAME',
    password = 'PASSWORD',
    persist = True
)
```

Instructions for setting up 2FA authorization are [here](https://github.com/Chavithra/degiro-connector#35-how-to-use-2fa-).

</details>

### EODHD

> Historical End of Day, Intraday, and Live prices API, with Fundamental Financial data API for more than 120000 stocks, ETFs and funds all over the world.

<details>
<summary>Instructions</summary>

Go to: https://eodhistoricaldata.com/r/?ref=869U7F4J

![EODHD](https://user-images.githubusercontent.com/46355364/207849214-23763c95-7314-42ae-b97d-cb5810686498.png)

Clicking on, "Registration", opens the page:

![EODHD](https://user-images.githubusercontent.com/46355364/207849324-00d4a916-8260-45c0-9714-289e0a0574c0.png)

Once registered, the API Key will be next to "API TOKEN".

![EODHD](https://user-images.githubusercontent.com/46355364/207849462-37471270-929a-45c5-a164-a84249b19231.png)

Enter this string into the OpenBB SDK with:

```console
openbb.keys.eodhd(key = 'REPLACE_WITH_KEY', persist = True)
```

</details>

### Finnhub

> With the sole mission of democratizing financial data, we are proud to offer a FREE realtime API for stocks, forex and cryptocurrency.

<details>
<summary>Instructions</summary>

Go to: https://finnhub.io/

![Finnhub](https://user-images.githubusercontent.com/46355364/207832028-283c3321-8c05-4ee8-b4d2-41cdc940f408.png)

Click on, "Get free api key", to open the page:

![Finnhub](https://user-images.githubusercontent.com/46355364/207832185-f4c8406a-3b75-4acc-b3e8-3c4b3272d4da.png)

Once the account has been created, find the API key in the account dashboard.

![Finnhub](https://user-images.githubusercontent.com/46355364/207832601-62007d95-410c-4d03-a5a3-b177d1894a4c.png)

Add this key to the OpenBB SDK with:

```console
openbb.keys.finnhub(key = 'REPLACE_WITH_KEY', persist = True)
```

</details>

### Financial Modeling Prep

> Enchance your application with our data that goes up to 30 years back in history. Earnings calendar, financial statements, multiple exchanges and more!

<details>
<summary>Instructions</summary>

Go to: https://site.financialmodelingprep.com/developer/docs

[FinancialModelingPrep](https://site.financialmodelingprep.com/developer/docs)

![FinancialModelingPrep](https://user-images.githubusercontent.com/46355364/207821920-64553d05-d461-4984-b0fe-be0368c71186.png)

Click on, "Get my API KEY here", and sign up for a free account.

![FinancialModelingPrep](https://user-images.githubusercontent.com/46355364/207822184-a723092e-ef42-4f87-8c55-db150f09741b.png)

With an account created, sign in and navigate to the Dashboard, which shows the assigned token. by pressing the "Dashboard" button which will show the API key.

![FinancialModelingPrep](https://user-images.githubusercontent.com/46355364/207823170-dd8191db-e125-44e5-b4f3-2df0e115c91d.png)

Enter the key into the OpenBB SDK with:

```console
openbb.keys.fmp(key = 'REPLACE_WITH_KEY', persist = True)
```

</details>

### FRED

> FRED is the trusted source for economic data since 1991. Download, graph, and track 819,000 US and international time series from 110 sources.

<details>
<summary>Instructions</summary>

Go to: https://fred.stlouisfed.org

![FRED](https://user-images.githubusercontent.com/46355364/207827137-d143ba4c-72cb-467d-a7f4-5cc27c597aec.png)

Click on, "My Account", create a new account or sign in with Google:

![FRED](https://user-images.githubusercontent.com/46355364/207827011-65cdd501-27e3-436f-bd9d-b0d8381d46a7.png)

After completing the sign-up, go to "My Account", and select "API Keys". Then, click on, "Request API Key".

![FRED](https://user-images.githubusercontent.com/46355364/207827577-c869f989-4ef4-4949-ab57-6f3931f2ae9d.png)

Fill in the box for information about the use-case for FRED, and by clicking, "Request API key", at the bottom of the page, the API key will be issued.

![FRED](https://user-images.githubusercontent.com/46355364/207828032-0a32d3b8-1378-4db2-9064-aa1eb2111632.png)

Enter the API key into the OpenBB SDK with:

```console
openbb.keys.fred(key = 'REPLACE_WITH_KEY', persist = True)
```

</details>

### GitHub

> GitHub is where over 100 million developers shape the future of software.

<details>
<summary>Instructions</summary>

![GitHub](https://user-images.githubusercontent.com/46355364/207846953-7feae777-3c3b-4f21-9dcf-84817c732618.png)

Sign up for, or sign in to, GitHub. Once logged in, navigate to the [apps](https://github.com/settings/apps) page, under account settings.

![GitHub](https://user-images.githubusercontent.com/46355364/207847215-3c04003f-26ea-4e62-9c13-ea35176bb5e3.png)

Select, "New GitHub App":

![GitHub](https://user-images.githubusercontent.com/46355364/207847383-d24416c6-18be-43f2-ae7c-455e8372a6ed.png)

After creating the app, the key will be issued. Enter this token into the OpenBB SDK with:

```console
openbb.keys.github(key = 'REPLACE_WITH_KEY', persist = True)
```

</details>

### Glassnode

> Glassnode makes blockchain data accessible for everyone. We source and carefully dissect on-chain data, to deliver contextualized and actionable insights.

<details>
<summary>Instructions</summary>

Go to: https://studio.glassnode.com

![Glassnode](https://user-images.githubusercontent.com/46355364/207843761-799078ff-fa64-4d39-a6eb-ba01d250be69.png)

Click on, "Sign up", and create an account:

![Glassnode](https://user-images.githubusercontent.com/46355364/207843795-dd2cdbdb-45eb-4c7d-b967-ae9857d4ea5d.png)

After creating an account, navigate to the [account settings](https://studio.glassnode.com/settings/api) and generate an API Key.

![Glassnode](https://user-images.githubusercontent.com/46355364/207843950-5f33f37d-0203-4302-a67f-198808f18e06.png)

Enter this key in the OpenBB SDK with:

```console
openbb.keys.glassnode(key = 'REPLACE_WITH_KEY', persist = True)
```

</details>

### Intrinio

> Intrinio is more than a financial data API provider – we're a real time data partner. That means we're your guide to every step of the financial data.

<details>
<summary>Instructions</summary>

Go to: https://intrinio.com/starter-plan

![Intrinio](https://user-images.githubusercontent.com/85772166/219207307-d6605460-ae2c-46d3-8b4e-f82057cfce59.png)

An API key will be issued with a subscription. Find the token value within the account dashboard, and enter it into the OpenBB SDK with:

```console
openbb.keys.intrinio(key = 'REPLACE_WITH_KEY', persist = True)
```

</details>

### Messari

> Gain an edge over the crypto market with professional grade data, tools, and research.

<details>
<summary>Instructions</summary>

Go to: https://messari.io

![Messari](https://user-images.githubusercontent.com/46355364/207848122-ec6a41e4-76b7-4620-adc3-1f1c19f4bca6.png)

Click on, "Sign up", and create an account.

![Messari](https://user-images.githubusercontent.com/46355364/207848160-6a962e3c-3007-40a3-9431-cd5ddfe5bb8e.png)

After creating the account, navigate to the [account page](https://messari.io/account/api), and click on the tab for, API Access.

![Messari](https://user-images.githubusercontent.com/46355364/207848324-ade5bede-8e6b-4b87-bdec-eade3217c0d8.png)

Copy the API key and add it to the OpenBB SDK with:

```console
openbb.keys.messari(key = 'REPLACE_WITH_KEY', persist = True)
```

</details>

### News API

> News API is a simple, easy-to-use REST API that returns JSON search results for current and historic news articles published by over 80,000 worldwide sources.

<details>
<summary>Instructions</summary>

Go to: https://newsapi.org

![News API](https://user-images.githubusercontent.com/46355364/207828250-0c5bc38c-90b4-427d-a611-b43c98c8e7ab.png)

Click on, "Get API Key", and fill out the form.

![News API](https://user-images.githubusercontent.com/46355364/207828421-76922bc2-cde0-493f-9eed-7f90eb831779.png)

Register for an account and the next screen will provide the API Key.

![News API](https://user-images.githubusercontent.com/46355364/207828736-f0fce53b-f302-4456-adf9-8d50ac41fbe2.png)

Add this API key into the OpenBB SDK with:

```console
openbb.keys.news(key = 'REPLACE_WITH_KEY', persist = True)
```

</details>

### Oanda

> OANDA's Currency Converter allows you to check the latest foreign exchange average bid/ask rates and convert all major world currencies.

<details>
<summary>Instructions</summary>

Go to: https://developer.oanda.com

![Oanda](https://user-images.githubusercontent.com/46355364/207839324-d30aa2b6-be83-41ff-9b1b-146cac566789.png)

After creating an account, follow the steps below.

![Oanda](https://user-images.githubusercontent.com/46355364/207839246-eb40f093-b583-4edd-b178-99fe399bfb66.png)

Upon completion of the account setup, enter the credentials into the OpenBB SDK with:

```console
openbb.keys.oanda(
    account = 'REPLACE_WITH_ACCOUNT',
    access_token = 'REPLACE_WITH_TOKEN',
    account_type = 'REPLACE_WITH_LIVE_OR_PRACTICE',
    persist = True
)
```

</details>

### Polygon

> Live & historical data for US stocks for all 19 exchanges. Instant access to real-time and historical stock market data.

<details>
<summary>Instructions</summary>

Go to: https://polygon.io

![Polygon](https://user-images.githubusercontent.com/46355364/207825623-fcd7f0a3-131a-4294-808c-754c13e38e2a.png)

Click on, "Get your Free API Key".

![Polygon](https://user-images.githubusercontent.com/46355364/207825952-ca5540ec-6ed2-4cef-a0ed-bb50b813932c.png)

After signing up, the API Key is found at the bottom of the account dashboard page.

![Polygon](https://user-images.githubusercontent.com/46355364/207826258-b1f318fa-fd9c-41d9-bf5c-fe16722e6601.png)

Enter the key into the OpenBB SDK with:

```console
openbb.keys.polygon(key = 'REPLACE_WITH_KEY', persist = True)
```

</details>

### Quandl

> The premier source for financial, economic, and alternative datasets, serving investment professionals. Quandl’s platform is used by over 400,000 people, including analysts from the world’s top hedge funds, asset managers and investment banks.

<details>
<summary>Instructions</summary>

![Quandl](https://user-images.githubusercontent.com/46355364/207823899-208a3952-f557-4b73-aee6-64ac00faedb7.png)

Click on, "Sign Up", and register a new account.

![Quandl](https://user-images.githubusercontent.com/46355364/207824214-4b6b2b74-e709-4ed4-adf2-14803e6f3568.png)

Follow the sign-up instructions, and upon completion the API key will be assigned.

![Quandl](https://user-images.githubusercontent.com/46355364/207824664-3c82befb-9c69-42df-8a82-510d85c19a97.png)

Enter the key into the OpenBB SDK with:

```console
openbb.keys.quandl(key = 'REPLACE_WITH_KEY', persist = True)
```

</details>

### Reddit

> Reddit is a network of communities where people can dive into their interests, hobbies and passions.

<details>
<summary>Instructions</summary>

Sign in to Reddit, and then go to: https://old.reddit.com/prefs/apps/

![Reddit](https://preview.redd.it/540vrn3k0cn91.png?width=986&format=png&auto=webp&v=enabled&s=88228cd0cf4415b3487b8d35e1097f0caa804e15)

Scroll down and click on "create application", selecting "script".

![Reddit](https://preview.redd.it/7je4ehqa1cn91.png?width=916&format=png&auto=webp&v=enabled&s=dbdf65ccc0820cfe28eff8e81cba056f4fd8263e)

Once the application is created, you must register it [here](https://old.reddit.com/wiki/api)

![Reddit](https://user-images.githubusercontent.com/46355364/207834105-665180be-c2b6-43c8-b1c9-477729905010.png)

Click on, "Read the full API terms and sign up for usage", and fill out the form.

![Reddit](https://user-images.githubusercontent.com/46355364/207834850-32a0d4c8-9990-4919-94e3-abad1487a3bd.png)

After submitting the form, check for a confirmation email. The credentials will be displayed [here](https://old.reddit.com/prefs/apps/), add them to the OpenBB SDK with:

```console
openbb.keys.reddit(
    client_id = 'REPLACE_WITH_CLIENT_ID',
    client_secret = 'REPLACE_WITH_CLIENT_SECRET',
    username = 'REPLACE_WITH_REDDIT_USERNAME',
    password = 'REPLACE_WITH_REDDIT_PASSWORD',
    useragent = 'REPLACE_WITH_USER_AGENT',
    persist = True
)
```

</details>

### Robinhood

> Robinhood has commission-free investing, and tools to help shape your financial future.

<details>
<summary>Instructions</summary>

Go to: https://robinhood.com/us/en

![Robinhood](https://user-images.githubusercontent.com/46355364/207838058-a2311632-6459-4cfd-bc0a-639ee3931574.png)

After registering for an account, it can be added to the OpenBB SDK with:

```console
openbb.keys.rb(
    username = 'REPLACE_WITH_USERNAME',
    password = 'REPLACE_WITH_PASSWORD',
    persist = True
```

The first login will request 2FA authorization from the device connected to the account.

</details>

### Santiment

> We provide tools to help you analyze crypto markets and find data-driven opportunities to optimize your investing.

<details>
<summary>Instructions</summary>

Go to: https://app.santiment.net

![Santiment](https://user-images.githubusercontent.com/46355364/207849709-a5f10b03-138c-4e09-89f6-8a18cfbaf008.png)

Click on, "Sign up", and register for an account.

![Santiment](https://user-images.githubusercontent.com/46355364/207849732-4bae61de-2f62-4919-b85d-f418f1bbd0c4.png)

Navigate to the [account dashboard](https://app.santiment.net/account#api-keys) and generate a key.

![Santiment](https://user-images.githubusercontent.com/46355364/207849839-31d1d0a7-6936-4ebd-a7f8-1292f6317b07.png)

Add it to the OpenBB SDK with:

```console
openbb.keys.santiment(key = 'REPLACE_WITH_KEY', persist = True)
```

</details>

### Stocksera

> Empowering investors to take advantage of alternative data. We track trending tickers on social media and provide alternative data for easy due-diligence & analysis.

<details>
<summary>Instructions</summary>

Go to: https://stocksera.pythonanywhere.com

![Stocksera](https://user-images.githubusercontent.com/46355364/207853896-ee233569-26bb-4244-b115-43ac8885757a.png)

Click on, "Log in", and create an account.

![Stocksera](https://user-images.githubusercontent.com/46355364/207853985-46a7a17f-b6b2-442b-886d-f68b3ba2ad5a.png)

Once logged in, navigate to the "Developers" tab and copy the API key.

![Stocksera](https://user-images.githubusercontent.com/46355364/207854224-e5ddace0-15d1-491c-b616-263cca0bef02.png)

Add the key to the OpenBB SDK with:

```console
openbb.keys.stocksera(key = 'REPLACE_WITH_KEY', persist = True)
```

</details>

### Token Terminal

> Token Terminal is a platform that aggregates financial data on the leading blockchains and decentralized applications.

<details>
<summary>Instructions</summary>

Go to: https://tokenterminal.com

![Token Terminal](https://user-images.githubusercontent.com/46355364/207850735-69368b4f-6a3e-46b8-ba69-3b79d9231f15.png)

Click on, "Log in" and sign up for an account.

![Token Terminal](https://user-images.githubusercontent.com/46355364/207850774-2071df78-3289-4c8e-9d64-156b9ec8ad81.png)

Verify the email address, and then navigate go to the "API" tab and copy the API key to the clipboard.

![Token Terminal](https://user-images.githubusercontent.com/46355364/207851035-71ea3eff-a11f-4835-8592-c07b3aa3f800.png)

Add the key to the OpenBB SDK with:

```console
openbb.keys.tokenterminal(key = 'REPLACE_WITH_KEY', persist = True)
```

</details>

### Tradier

> Tradier, the home of active traders. Our open collaboration platform allows investors to truly customize their trading experience like never before.

<details>
<summary>Instructions</summary>

Go to: https://documentation.tradier.com

![Tradier](https://user-images.githubusercontent.com/46355364/207829178-a8bba770-f2ea-4480-b28e-efd81cf30980.png)

Click on, "Open Account", to start the sign-up process. After the account has been setup, navigate to [Tradier Broker Dash](https://dash.tradier.com/login?redirect=settings.api) and create the application. Request a sandbox access token, and enter this key into the OpenBB SDK with:

```console
openbb.keys.tradier(key = 'REPLACE_WITH_KEY', persist = True)
```

</details>

### Twitter

> From breaking news and entertainment to sports and politics, get the full story with all the live commentary.

<details>
<summary>Upcoming changes to the Twitter API will deprecate the current functionality, it is uncertain if the features will continue to work. </summary>

![Twitter API](https://pbs.twimg.com/media/FooIJF3agAIU8SN?format=png&name=medium)

</details>

### Whale Alert

> Whale Alert continuously collects and analyzes billions of blockchain transactions and related-off chain data from hundreds of reliable sources and converts it into an easy to use standardized format. Our world-class analytics and custom high speed database solutions process transactions the moment they are made, resulting in the largest and most up-to-date blockchain dataset in the world.

<details>
<summary>Instructions</summary>

Go to: https://docs.whale-alert.io
![Whale Alert](https://user-images.githubusercontent.com/46355364/207842892-3f71ee7a-6cd3-48a2-82e4-fa5ec5b13807.png)

Click on, "sign up here".

![Whale Alert](https://user-images.githubusercontent.com/46355364/207842992-427f1d2c-b34e-41c9-85fd-18511805fd16.png)

After creating the account, click on, "Create", to issue the API Key.

![Whale Alert](https://user-images.githubusercontent.com/46355364/207843214-20232465-9a52-4b66-b01a-0b8cecbdd612.png)

Enter the key into the OpenBB SDK with:

```console
openbb.keys.walert(key = 'REPLACE_WITH_KEY', persist = True)
```

</details>
