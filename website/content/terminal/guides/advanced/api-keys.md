---
title: Set API keys
sidebar_position: 1
---
## Accessing the keys menu
Within the `keys` menu you can define your, often free, API key from various platforms like Alpha Vantage, FRED, IEX, Twitter, DeGiro, Binance and Coinglass. An API key is a set of random characters provided to you by a third party vendor that allows you to access data via their API endpoints.

You can access this menu from the homepage with `keys` which will open the menu as shown below:

<img width="800" alt="image" src="https://user-images.githubusercontent.com/85772166/194684312-f12b7f26-8a04-4efe-bc94-fa516b7186d3.png"></img>

Within this menu you are able to set your API keys to access the commands that require that key. You can do so by typing the command followed by the API key, for example: `fred a215egade08a8d47cfd49c849658a2be`. When you press `ENTER` (⏎) the terminal will test whether this API key works. If it does, you receive the message `defined, test passed` and if it does not, you receive the message `defined, test failed`.

To figure out where you can obtain the API key, you can enter the command (e.g. `av`) and press `ENTER` (⏎) or use the table below. **We recommend that you gradually obtain and set keys whenever you wish to use features that require an API key. For example, if you are interested in viewing recent news about a company, you should set the API key from the 'News API'.**

<details>
<summary>Summary of API Key Providers</summary>

| Command    | Name                                     | URL                                                                                |
| :--------- | :--------------------------------------- | :--------------------------------------------------------------------------------- |
| av         | AlphaVantage                             | https://www.alphavantage.co/support/#api-key                                       |
| binance    | Binance                                  | https://binance.com                                                                |
| bitquery   | Bitquery                                 | https://bitquery.io/                                                               |
| cmc        | CoinMarketCap                            | https://coinmarketcap.com/api/                                                     |
| cb         | Coinbase                                 | https://help.coinbase.com/en/exchange/managing-my-account/how-to-create-an-api-key |
| coinglass  | Coinglass                                | https://coinglass.github.io/API-Reference/#api-key                                 |
| cpanic     | Crypto Panic                             | https://cryptopanic.com/developers/api/                                            |
| degiro     | DeGiro                                   | https://www.degiro.com/                                                            |
| eodhd      | EODHD                                    | https://eodhistoricaldata.com/                                                     |
| ethplorer  | Ethplorer                                | https://github.com/EverexIO/Ethplorer/wiki/Ethplorer-API                           |
| finnhub    | Finnhub                                  | https://finnhub.io/                                                                |
| fmp        | Financial Modelling Prep                 | https://site.financialmodelingprep.com/developer/docs/                             |
| fred       | Federal Reserve Economic Database (FRED) | https://fred.stlouisfed.org                                                        |
| github     | GitHub                                   | https://docs.github.com/en/rest/guides/getting-started-with-the-rest-api           |
| glassnode  | Glassnode                                | https://docs.glassnode.com/basic-api/api-key#how-to-get-an-api-key/                |
| iex        | IEX Cloud                                | https://iexcloud.io/                                                               |
| messari    | Messari                                  | https://messari.io/api/docs                                                        |
| news       | News API                                 | https://newsapi.org/                                                               |
| oanda      | Oanda                                    | https://developer.oanda.com                                                        |
| polygon    | Polygon                                  | https://polygon.io                                                                 |
| quandl     | Quandl                                   | https://www.quandl.com                                                             |
| reddit     | Reddit                                   | https://www.reddit.com/wiki/api                                                    |
| rh         | Robinhood                                | https://robinhood.com/us/en/                                                       |
| santiment  | Santiment                                | https://app.santiment.net/                                                         |
| shroom     | ShroomDK                                 | https://sdk.flipsidecrypto.xyz/shroomdk                                            |
| smartstake | Smartstake                               | https://www.smartstake.io                                                          |
| stocksera  | Stocksera                                | https://stocksera.pythonanywhere.com/                                              |
| tokenterminal    | Token Terminal                     | https://tokenterminal.com/                                                         |
| tradier    | Tradier                                  | https://documentation.tradier.com/                                                 |
| twitter    | Twitter                                  | https://developer.twitter.com                                                      |
| si         | Sentiment Investor                       | https://sentimentinvestor.com                                                      |
| walert     | Whale Alert                              | https://docs.whale-alert.io/                                                       |
</details>

## How to obtain the API Key from each source
This section covers all API keys listed above and include detailed instructions how to obtain each API key. By clicking on each name, the section will expand and instructions are provided.

<details>
<summary>AlphaVantage</summary>

Go to https://www.alphavantage.co/support/#api-key. You will be greeted with the following screen:

<img width="500" alt="image" src="https://user-images.githubusercontent.com/46355364/207820936-46c2ba00-81ff-4cd3-98a4-4fa44412996f.png"></img>

Once you enter the type of investor you are, the organization you work at and your email address pressing "GET FREE API KEY" gets you the key that you can submit into the OpenBB Terminal with `/keys/av KEY`

</details>

<details>
<summary>Binance</summary>

Go to https://www.binance.com/en/support/faq/how-to-create-api-360002502072. You will be greeted with the following screen:

<img width="500" alt="image" src="https://user-images.githubusercontent.com/46355364/207839805-f71cf12a-62d2-41cb-ba19-0c35917abc40.png"></img>

These instructions should provide clear guidance how to set up an API Key. Enter this API key into the OpenBB Terminal by typing `/keys/binance -k KEY -s SECRET`.
 </details> 
 
<details>
<summary>Bitquery</summary>

Go to https://bitquery.io/. You will be greeted with the following screen:

<img width="500" alt="image" src="https://user-images.githubusercontent.com/46355364/207840322-5532a3f9-739f-4e28-9839-a58db932882e.png"></img>

Click "Try GraphQL API". This opens the following screen:

<img width="500" alt="image" src="https://user-images.githubusercontent.com/46355364/207840576-2c51a538-dd9b-484d-b11d-40e3e424df62.png"></img>

After creating an account and verifying your email address, you will be able to access your API Key by clicking "Api Key". Enter this API key into the OpenBB Terminal by typing `/keys/bitquery KEY`.

<img width="500" alt="image" src="https://user-images.githubusercontent.com/46355364/207840833-35c1b12c-9b4b-43fe-a33e-f7b92c43a011.png"></img>
 </details> 
  
<details>
<summary>CoinMarketCap</summary>

Go to https://coinmarketcap.com/api. You will be greeted with the following screen:

<img width="500" alt="image" src="https://user-images.githubusercontent.com/46355364/207831111-3f09ed75-740e-4121-a67e-6e1f36e8ab9a.png"></img>

From here, click "Get Your Free API Key Now". This opens up the following screen:

<img width="500" alt="image" src="https://user-images.githubusercontent.com/46355364/207831345-06a48efe-63b2-4804-bcf9-52fa4a73f7db.png"></img>

Once you have created an account, you will be able to find your API key in the following screen. Enter this API key into the OpenBB Terminal by typing `/keys/cmc KEY`

<img width="500" alt="image" src="https://user-images.githubusercontent.com/46355364/207831705-e9f95018-bba7-49a9-b057-3443bc839861.png"></img>
 </details> 
  
<details>
<summary>CoinBase</summary>

Go to https://help.coinbase.com/en/exchange/managing-my-account/how-to-create-an-api-key. You will be greeted with the following screen:

<img width="500" alt="image" src="https://user-images.githubusercontent.com/46355364/207841901-647f0aef-0c74-454d-b99e-367d784259f0.png"></img>

By following these instructions you should be able to set-up an API Key. Enter this API key into the OpenBB Terminal by typing `/keys/coinbase -k KEY -s SECRET -p PASSPHRASE`.
 </details> 

<details>
<summary>Coinglass</summary>

Go to https://www.coinglass.com/. You will be greeted with the following screen:

<img width="500" alt="image" src="https://user-images.githubusercontent.com/46355364/207844601-8510687a-e54f-49b9-961f-5ef6718f58ab.png"></img>

Click "Log in" and sign up for an account. This opens up the following screen:

<img width="500" alt="image" src="https://user-images.githubusercontent.com/46355364/207844637-a9321889-c4d8-4d44-95fe-a6288a17ad19.png"></img>

Once you created your account, you will be able to find the API Key on your profile. Enter this API key into the OpenBB Terminal by typing `/keys/coinglass KEY`.
 </details> 

<details>
<summary>Crypto Panic</summary>

Go to https://cryptopanic.com/developers/api/. You will be greeted with the following screen:

<img width="500" alt="image" src="https://user-images.githubusercontent.com/46355364/207848733-27e5a804-7ae7-4ca2-88b2-848b32929b6f.png"></img>

Click "Sign up" under "Your free API auth token". This opens up the following screen:

<img width="500" alt="image" src="https://user-images.githubusercontent.com/46355364/207848825-8b2095ed-21ef-4f8e-b176-c2e9bdf42ba5.png"></img>

Once you have created your account, your API Key will be displayed under "Your free API auth token". Enter this API key into the OpenBB Terminal by typing `/keys/cpanic KEY`.

<img width="500" alt="image" src="https://user-images.githubusercontent.com/46355364/207848971-3e4771b7-1faa-45fe-955f-81bd736b16b7.png"></img>
 </details> 
 
<details>
<summary>DeGiro</summary>

Go to https://www.degiro.com/. You will be greeted with the following screen:

<img width="500" alt="image" src="https://user-images.githubusercontent.com/46355364/207838353-001d350c-872c-4770-a586-fb21318122eb.png"></img>

Click "Sign up" and go to the registrations process. After setting up your account you will be able to use this broker by entering your username and password in the OpenBB Terminal as follows `/keys/degiro -u USERNAME -p PASSWORD`. We also support 2FA, you can find more information about that [here](https://github.com/Chavithra/degiro-connector#35-how-to-use-2fa-).
 </details> 

<details>
<summary>EODHD</summary>

Go to https://eodhistoricaldata.com/. You will be greeted with the following screen:

<img width="500" alt="image" src="https://user-images.githubusercontent.com/46355364/207849214-23763c95-7314-42ae-b97d-cb5810686498.png"></img>

Click "Registration". This opens up the following screen:

<img width="500" alt="image" src="https://user-images.githubusercontent.com/46355364/207849324-00d4a916-8260-45c0-9714-289e0a0574c0.png"></img>

Once you have registered, you can find the API Key next to "API TOKEN". Enter this API key into the OpenBB Terminal by typing `/keys/cpanic KEY`.

<img width="500" alt="image" src="https://user-images.githubusercontent.com/46355364/207849462-37471270-929a-45c5-a164-a84249b19231.png"></img>
</details>

<details>
<summary>Finnhub</summary>

Go to https://finnhub.io/. You will be greeted with the following screen:

<img width="500" alt="image" src="https://user-images.githubusercontent.com/46355364/207832028-283c3321-8c05-4ee8-b4d2-41cdc940f408.png"></img>

Press "Get free api key". This opens up the following screen:

<img width="500" alt="image" src="https://user-images.githubusercontent.com/46355364/207832185-f4c8406a-3b75-4acc-b3e8-3c4b3272d4da.png"></img>

Once you have created an account, you will be able to find your API key in the following screen. Enter this API key into the OpenBB Terminal by typing `/keys/finnhub KEY`

<img width="500" alt="image" src="https://user-images.githubusercontent.com/46355364/207832601-62007d95-410c-4d03-a5a3-b177d1894a4c.png"></img>
</details>

<details>
<summary>Financial Modelling Prep</summary>

Go to  https://site.financialmodelingprep.com/developer/docs/. You will be greeted with the following screen:

<img width="500" alt="image" src="https://user-images.githubusercontent.com/46355364/207821920-64553d05-d461-4984-b0fe-be0368c71186.png"></img>

From here, press "Get my API KEY here". This opens up the following screen:

<img width="500" alt="image" src="https://user-images.githubusercontent.com/46355364/207822184-a723092e-ef42-4f87-8c55-db150f09741b.png"></img>

If you already have an account, you can sign-in directly and obtain the API key, otherwise click "Sign Up". Once you have created an account you can access your API Key by pressing the "Dashboard" button which will show the API key. Enter this API key into the OpenBB Terminal by typing `/keys/fmp KEY`

<img width="500" alt="image" src="https://user-images.githubusercontent.com/46355364/207823170-dd8191db-e125-44e5-b4f3-2df0e115c91d.png"></img>
</details>

<details>
<summary>FRED</summary> 

Go to https://fred.stlouisfed.org. You will be greeted with the following screen:

<img width="500" alt="image" src="https://user-images.githubusercontent.com/46355364/207827137-d143ba4c-72cb-467d-a7f4-5cc27c597aec.png"></img>

Click on "My Account". This opens up the following screen:

<img width="500" alt="image" src="https://user-images.githubusercontent.com/46355364/207827011-65cdd501-27e3-436f-bd9d-b0d8381d46a7.png"></img>

Once you have signed up, go to "My Account" and select "API Keys". This will get you to the following screen:

<img width="500" alt="image" src="https://user-images.githubusercontent.com/46355364/207827577-c869f989-4ef4-4949-ab57-6f3931f2ae9d.png"></img>

Click on "Request API Key" and fill in information about why you wish to use FRED. Then, by pressing "Request API key" you will be able to obtain the API key. Enter this API key into the OpenBB Terminal by typing `/keys/fred KEY`

<img width="500" alt="image" src="https://user-images.githubusercontent.com/46355364/207828032-0a32d3b8-1378-4db2-9064-aa1eb2111632.png"></img>
</details>

<details>
<summary>GitHub</summary> 

Go to https://github.com/. You will be greeted with the following screen:

<img width="500" alt="GitHub" src="https://user-images.githubusercontent.com/46355364/207846953-7feae777-3c3b-4f21-9dcf-84817c732618.png"></img>

Click "Sign up" and create an account with GitHub. Once you have done so go to as depicted below: https://github.com/settings/apps

<img width="500" alt="image" src="https://user-images.githubusercontent.com/46355364/207847215-3c04003f-26ea-4e62-9c13-ea35176bb5e3.png"></img>

Press "New GitHub App". This opens up the following screen:

<img width="500" alt="image" src="https://user-images.githubusercontent.com/46355364/207847383-d24416c6-18be-43f2-ae7c-455e8372a6ed.png"></img>

Once the app is created you are able to obtain the API Key. Enter this API key into the OpenBB Terminal by typing `/keys/github KEY`.
</details>

<details>
<summary>Glassnode</summary> 

Go to https://studio.glassnode.com/. You will be greeted with the following screen:

<img width="500" alt="image" src="https://user-images.githubusercontent.com/46355364/207843761-799078ff-fa64-4d39-a6eb-ba01d250be69.png"></img>

Click on "Sign up". This opens up the following screen:

<img width="500" alt="image" src="https://user-images.githubusercontent.com/46355364/207843795-dd2cdbdb-45eb-4c7d-b967-ae9857d4ea5d.png"></img>

After you have created your account, go to https://studio.glassnode.com/settings/api where you can create your API Key. Enter this API key into the OpenBB Terminal by typing `/keys/glassnode KEY`.

<img width="500" alt="image" src="https://user-images.githubusercontent.com/46355364/207843950-5f33f37d-0203-4302-a67f-198808f18e06.png"></img>
</details>

<details>
<summary>IEX Cloud</summary> 

Go to https://iexcloud.io/. You will be greeted with the following screen:

<img width="500" alt="image" src="https://user-images.githubusercontent.com/46355364/207833088-e879e9f2-3180-4e50-ba9e-f40ee958f98a.png"></img>

Press "Sign in". This opens up the following screen:

<img width="500" alt="image" src="https://user-images.githubusercontent.com/46355364/207833011-542d6ef0-0bdf-494a-83cb-c0a6741df2a3.png"></img>

Once you have signed up you are asked what kind of plan you would like. You have the option to start a free plan at the bottom.

<img width="500" alt="image" src="https://user-images.githubusercontent.com/46355364/207833303-4ebb2880-0b4c-4008-9b33-0e8ee6836027.png"></img>

Once you have confirmed you email address, you can find your API Key under "Access & Security". Enter this API key into the OpenBB Terminal by typing `/keys/iex KEY`

<img width="500" alt="image" src="https://user-images.githubusercontent.com/46355364/207833540-c1e25500-22e9-43c3-a89e-b05dd446f2a5.png"></img>
</details>

<details>
<summary>Messari</summary> 

Go to https://messari.io/. You will be greeted with the following screen:

<img width="500" alt="image" src="https://user-images.githubusercontent.com/46355364/207848122-ec6a41e4-76b7-4620-adc3-1f1c19f4bca6.png"></img>

Press "Sign up". This opens up the following screen:

<img width="500" alt="image" src="https://user-images.githubusercontent.com/46355364/207848160-6a962e3c-3007-40a3-9431-cd5ddfe5bb8e.png"></img>

Once you have signed up, go to https://messari.io/account/api where you will be able to find your API Key. Enter this API key into the OpenBB Terminal by typing `/keys/messari KEY`.

<img width="500" alt="image" src="https://user-images.githubusercontent.com/46355364/207848324-ade5bede-8e6b-4b87-bdec-eade3217c0d8.png"></img>
</details>

<details>
<summary>News API</summary> 

Go to https://newsapi.org/. You will be greeted with the following screen:

<img width="500" alt="image" src="https://user-images.githubusercontent.com/46355364/207828250-0c5bc38c-90b4-427d-a611-b43c98c8e7ab.png"></img>

Press "Get API Key". This opens up the following screen:

<img width="500" alt="image" src="https://user-images.githubusercontent.com/46355364/207828421-76922bc2-cde0-493f-9eed-7f90eb831779.png"></img>

Register for an account. The next screen will provide you with the API Key. Enter this API key into the OpenBB Terminal by typing `/keys/news KEY`

<img width="500" alt="image" src="https://user-images.githubusercontent.com/46355364/207828736-f0fce53b-f302-4456-adf9-8d50ac41fbe2.png"></img>
</details>

<details>
<summary>Oanda</summary> 

Go to https://developer.oanda.com. You will be greeted with the following screen:

<img width="500" alt="image" src="https://user-images.githubusercontent.com/46355364/207839324-d30aa2b6-be83-41ff-9b1b-146cac566789.png"></img>

After you have created an account with Oanda, you will be able to find the API key by following the steps below. After setting up your account you will be able to use this broker by entering your username and password in the OpenBB Terminal as follows `/keys/oanda -a ACCOUNT -t TOKEN`.

<img width="500" alt="image" src="https://user-images.githubusercontent.com/46355364/207839246-eb40f093-b583-4edd-b178-99fe399bfb66.png"></img>
</details>

<details>
<summary>Polygon</summary> 

Go to https://polygon.io. You will be greeted with the following screen:

<img width="500" alt="image" src="https://user-images.githubusercontent.com/46355364/207825623-fcd7f0a3-131a-4294-808c-754c13e38e2a.png"></img>

Press the button "Get your Free API Key". This opens up the following screen:

<img width="500" alt="image" src="https://user-images.githubusercontent.com/46355364/207825952-ca5540ec-6ed2-4cef-a0ed-bb50b813932c.png"></img>

Once signed up you will find the API Key at the bottom. Enter this API key into the OpenBB Terminal by typing `/keys/polygon KEY`

<img width="500" alt="image" src="https://user-images.githubusercontent.com/46355364/207826258-b1f318fa-fd9c-41d9-bf5c-fe16722e6601.png"></img>
</details>
  
<details>
<summary>Quandl</summary> 

Go to https://www.quandl.com. You will be greeted with the following screen:

<img width="500" alt="image" src="https://user-images.githubusercontent.com/46355364/207823899-208a3952-f557-4b73-aee6-64ac00faedb7.png"></img>

From here, click "Sign Up" at the top. This opens up the following screen:

<img width="500" alt="image" src="https://user-images.githubusercontent.com/46355364/207824214-4b6b2b74-e709-4ed4-adf2-14803e6f3568.png"></img>

Follow the sign-up instructions and once you have signed up you will be able to retrieve your API key. Enter this API key into the OpenBB Terminal by typing `/keys/quandl KEY`

<img width="500" alt="image" src="https://user-images.githubusercontent.com/46355364/207824664-3c82befb-9c69-42df-8a82-510d85c19a97.png"></img>
</details>

<details>
<summary>Reddit</summary> 

Go to https://www.reddit.com/wiki/api. You will be greeted with the following screen:

<img width="500" alt="image" src="https://user-images.githubusercontent.com/46355364/207834105-665180be-c2b6-43c8-b1c9-477729905010.png"></img>

Press "Read the full API terms and sign up for usage" and start the sign-up process. This opens up the following screen:

<img width="500" alt="image" src="https://user-images.githubusercontent.com/46355364/207834850-32a0d4c8-9990-4919-94e3-abad1487a3bd.png"></img>

Once you have filled out everything, you will receive an email when your application is approved. Once this is approved you will receive the necessary information that needs to be entered in the OpenBB Terminal. Enter these into the OpenBB Terminal by typing `/keys/reddit -i CLIENT_ID -s CLIENT_SECRET -u USERNAME -p PASSWORD -a USER_AGENT`.
</details>

<details>
<summary>Robinhood</summary> 

Go to https://robinhood.com/us/en/. You will be greeted with the following screen:

<img width="500" alt="image" src="https://user-images.githubusercontent.com/46355364/207838058-a2311632-6459-4cfd-bc0a-639ee3931574.png"></img>

Click "Sign up" and go to the registrations process. After setting up your account you will be able to use this broker by entering your username and password in the OpenBB Terminal as follows `/keys/rb -u USERNAME -p PASSWORD`.
</details>

<details>
<summary>Santiment</summary> 

Go to https://app.santiment.net/. You will be greeted with the following screen:

<img width="500" alt="image" src="https://user-images.githubusercontent.com/46355364/207849709-a5f10b03-138c-4e09-89f6-8a18cfbaf008.png"></img>

Click "Sign up". This opens up the following screen:

<img width="500" alt="image" src="https://user-images.githubusercontent.com/46355364/207849732-4bae61de-2f62-4919-b85d-f418f1bbd0c4.png"></img>

After creating an account go to https://app.santiment.net/account#api-keys and generate a key. Enter this API key into the OpenBB Terminal by typing `/keys/santiment KEY`.

<img width="500" alt="image" src="https://user-images.githubusercontent.com/46355364/207849839-31d1d0a7-6936-4ebd-a7f8-1292f6317b07.png"></img>
</details>

<details>
<summary>ShroomDK</summary> 

Go to https://app.santiment.net/. You will be greeted with the following screen:

<img width="500" alt="image" src="https://user-images.githubusercontent.com/46355364/207850122-b8cd225e-0a65-4ea8-8069-0b40fff1600e.png"></img>

Click "Mint Your ShroomDK API Key" and sign up for an account. This opens up the following screen:

<img width="500" alt="image" src="https://user-images.githubusercontent.com/46355364/207850176-f29cc73b-2b55-46e8-bce3-62c9342b6599.png"></img>

Once you have your account created, connect a wallet and access the API Key. Enter this API key into the OpenBB Terminal by typing `/keys/shroom KEY`.

<img width="500" alt="image" src="https://user-images.githubusercontent.com/46355364/207850380-b59554af-1e65-4616-921d-e02c9ecf1aad.png"></img>
</details>

<details>
<summary>Stocksera</summary> 

Go to https://stocksera.pythonanywhere.com/. You will be greeted with the following screen:

<img width="500" alt="image" src="https://user-images.githubusercontent.com/46355364/207853896-ee233569-26bb-4244-b115-43ac8885757a.png"></img>

Click "Log in" and create an account. This opens up the following screen:

<img width="500" alt="image" src="https://user-images.githubusercontent.com/46355364/207853985-46a7a17f-b6b2-442b-886d-f68b3ba2ad5a.png"></img>

Once you have created an account, go to "Developers" to access your API Key. Enter this API key into the OpenBB Terminal by typing `/keys/stocksera KEY`.

<img width="500" alt="image" src="https://user-images.githubusercontent.com/46355364/207854224-e5ddace0-15d1-491c-b616-263cca0bef02.png"></img>
</details>

<details>
<summary>Token Terminal</summary> 

Go to  https://tokenterminal.com/. You will be greeted with the following screen:

<img width="500" alt="image" src="https://user-images.githubusercontent.com/46355364/207850735-69368b4f-6a3e-46b8-ba69-3b79d9231f15.png"></img>

Click "Log in" and sign up for an account. This opens up the following screen:

<img width="500" alt="image" src="https://user-images.githubusercontent.com/46355364/207850774-2071df78-3289-4c8e-9d64-156b9ec8ad81.png"></img>

Once you have created an account, go to "API" to access your API Key. Enter this API key into the OpenBB Terminal by typing `/keys/tokenterminal KEY`.

<img width="500" alt="image" src="https://user-images.githubusercontent.com/46355364/207851035-71ea3eff-a11f-4835-8592-c07b3aa3f800.png"></img>
</details>

<details>
<summary>Tradier</summary> 

Go to https://documentation.tradier.com/. You will be greeted with the following screen:

<img width="500" alt="image" src="https://user-images.githubusercontent.com/46355364/207829178-a8bba770-f2ea-4480-b28e-efd81cf30980.png"></img>

Click the button "Open Account" and start the sign-up process. Once you have gone through the whole process you will be able to find your API key within your account. Enter this API key into the OpenBB Terminal by typing `/keys/tradier KEY`
</details>

<details>
<summary>Twitter</summary> 

Go to https://developer.twitter.com. You will be greeted with the following screen:

<img width="500" alt="image" src="https://user-images.githubusercontent.com/46355364/207835646-bb05ac60-2685-48a5-8ffb-e08225db1156.png"></img>

Click "Sign Up". Note that you are required to have a Twitter account and that you have verified your phone number. This opens up the following screen:

<img width="500" alt="image" src="https://user-images.githubusercontent.com/46355364/207836277-ad523657-181a-4b01-ae68-398d2bcd39c7.png"></img>

Create an account and verify your email. Then, you will be able to create an app to obtain your API Key.

<img width="500" alt="image" src="https://user-images.githubusercontent.com/46355364/207837349-1bf2a15d-9502-48b8-aa38-08040cdebc06.png"></img>

This will give you the following keys. Enter these into the OpenBB Terminal by typing `/keys/twitter -k API_KEY -s API_KEY_SECRET -t BEARER_TOKEN`.

<img width="500" alt="image" src="https://user-images.githubusercontent.com/46355364/207837560-1d04a5da-eba7-425d-afff-6fcc8cbe003e.png"></img>
</details>

<details>
<summary>Whale Alert</summary> 

Go to https://docs.whale-alert.io/. You will be greeted with the following screen:

<img width="500" alt="image" src="https://user-images.githubusercontent.com/46355364/207842892-3f71ee7a-6cd3-48a2-82e4-fa5ec5b13807.png"></img>

Click "sign up here". This opens up the following screen:

<img width="500" alt="image" src="https://user-images.githubusercontent.com/46355364/207842992-427f1d2c-b34e-41c9-85fd-18511805fd16.png"></img>

Once you have created your account, click "Create" to create your own API Key. Enter this API key into the OpenBB Terminal by typing `/keys/walert KEY`.

<img width="500" alt="image" src="https://user-images.githubusercontent.com/46355364/207843214-20232465-9a52-4b66-b01a-0b8cecbdd612.png"></img>
</details>
