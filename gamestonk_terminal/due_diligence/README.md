# DUE DILIGENCE

This menu aims to help in due-diligence of a pre-loaded stock, and the usage of the following commands along with an example will be exploited below.

* [news](#news)
  * latest news of the company [News API]
* [red](#red)
  * gets due diligence from another user's post [Reddit]
* [analyst](#analyst)
  * analyst prices and ratings of the company [Finviz]
* [rating](#rating)
  * rating of the company from strong sell to strong buy [FMP]
* [pt](#pt)
  * price targets over time [Business Insider]
* [rot](#rot)
  * ratings over time [Finnhub]
* [est](#est)
  * quarter and year analysts earnings estimates [Business Insider]
* [ins](#ins)
  * insider activity over time [Business Insider]
* [insider](#insider)
  * insider trading of the company [Finviz]
* [sec](#sec)
  * SEC filings [Market Watch]
* [short](#short)
  * short interest [Quandl]
* [warnings](#warnings)
  * company warnings according to Sean Seah book [Market Watch]
* [dp](#dp)
  * dark pools (ATS) vs OTC data [FINRA]
* [ftd](#ftd)
  * fails-to-deliver data [SEC]
* [shortview](#shortview)
  * shows price vs short interest volume [Stockgrid]
* [darkpos](#darkpos)
  * net short vs position [Stockgrid]
* [supplier](#supplier)
  * list of suppliers [csimarket]
* [customer](#customer)
  * list of customers [csimarket]

## news <a name="news"></a>

```text
news [-n N_NUM]
```

Prints latest news about company, including date, title and web link. [Source: News API]

* -n : Number of latest news being printed. Default 10.

<img width="770" alt="Captura de ecrã 2021-03-22, às 22 47 42" src="https://user-images.githubusercontent.com/25267873/112070935-b2587a00-8b66-11eb-8dfb-0353fc83311d.png">


## red <a name="red"></a>

```text
usage: red [-l N_LIMIT] [-d N_DAYS] [-a]
```

Print top stock's due diligence from other users. [Source: Reddit]

* -l : limit of posts to retrieve
* -d : number of prior days to look for
* -a : "search through all flairs (apart from Yolo and Meme). Default False (i.e. use flairs: DD, technical analysis, Catalyst, News, Advice, Chart)

<img width="950" alt="red" src="https://user-images.githubusercontent.com/25267873/108609417-a2ae1000-73c5-11eb-8f3c-54c76b418e14.png">

## analyst <a name="analyst"></a>

```text
usage: analyst
```

Print analyst prices and ratings of the company. The following fields are expected: date, analyst, category, price from, price to, and rating. [Source: Finviz]

<img width="938" alt="analyst" src="https://user-images.githubusercontent.com/25267873/108609253-a8572600-73c4-11eb-9629-6c192fc2907c.png">

## rating <a name="rating"></a>

```text
usage: rating
```

Based on specific ratios, prints information whether the company is a (strong) buy, neutral or a (strong) sell. The following fields are expected: P/B, ROA, DCF, P/E, ROE, and D/E. [Source: Financial Modeling Prep]
<img width="922" alt="rating" src="https://user-images.githubusercontent.com/25267873/108609444-d0935480-73c5-11eb-9f14-4fefa67f41ee.png">

## pt <a name="pt"></a>

```text
usage: pt [-n N_NUM]
```

Prints price target from analysts. [Source: Business Insider]

* -n : number of latest price targets from analysts to print. Default 10.

![pt](https://user-images.githubusercontent.com/25267873/108609888-fec66380-73c8-11eb-8c2f-04ceaac6f3f5.png)

<img width="940" alt="pt2" src="https://user-images.githubusercontent.com/25267873/108609914-3af9c400-73c9-11eb-8820-0abfa9e57119.png">


## rot <a name="rot"></a>

```text
usage: rot
```

Plots ratings over time. [Source: Finnhub]

![rot](https://user-images.githubusercontent.com/25267873/116864981-ad282980-ac00-11eb-9e86-7163782a8ef6.png)


## est <a name="est"></a>

```text
usage: est
```

Yearly estimates and quarter earnings/revenues [Source: Business Insider]

<img width="933" alt="est" src="https://user-images.githubusercontent.com/25267873/108609498-3089fb00-73c6-11eb-991d-656d69beb685.png">

## ins <a name="ins"></a>

```text
usage: ins [-n N_NUM]
```

Prints insider activity over time [Source: Business Insider]
* -n : number of latest insider activity. Default 10.

![ins](https://user-images.githubusercontent.com/25267873/108609248-a725f900-73c4-11eb-9442-1ba3a0bf45ba.png)
<img width="935" alt="ins2" src="https://user-images.githubusercontent.com/25267873/108609249-a7be8f80-73c4-11eb-8685-1cddbed5421e.png">

## insider <a name="insider"></a>

```text
usage: insider [-n N_NUM]
```

Prints information about inside traders. The following fields are expected: Date, Relationship, Transaction, #Shares, Cost, Value ($), #Shares Total, Insider Trading, SEC Form 4. [Source: Finviz]

* -n : number of latest inside traders. Default 5.

<img width="937" alt="insider" src="https://user-images.githubusercontent.com/25267873/108609258-a9885300-73c4-11eb-971e-ce84ee9dd94b.png">

## sec <a name="sec"></a>

```text
usage: sec [-n N_NUM]
```

Prints SEC filings of the company. The following fields are expected: Filing Date, Document Date, Type, Category, Amended, and Link. [Source: Market Watch]

* -n : number of latest SEC filings. Default 5.

<img width="967" alt="sec" src="https://user-images.githubusercontent.com/25267873/108609256-a8efbc80-73c4-11eb-97cc-3c819aebc795.png">

## short <a name="short"></a>

```text
usage: short [-n] [-d N_DAYS]
```

Plots the short interest of a stock. This corresponds to the number of shares that have been sold short but have not yet been covered or closed out. [Source: Quandl]

* -n : data from NYSE flag. Default False (i.e. NASDAQ).
* -d : number of latest days to print data. Default 10.

![short](https://user-images.githubusercontent.com/25267873/108609247-a68d6280-73c4-11eb-80b3-b8effa6988f1.png)
<img width="967" alt="short2" src="https://user-images.githubusercontent.com/25267873/108609259-a9885300-73c4-11eb-9f37-64b78746cec3.png">

## warnings <a name="warnings"></a>

```text
usage: warnings [-i] [-d]
```

Sean Seah warnings. Check: Consistent historical earnings per share; Consistently high return on equity; Consistently high return on assets; 5x Net Income > Long-Term Debt; and Interest coverage ratio more than 3. See <https://www.drwealth.com/gone-fishing-with-buffett-by-sean-seah/comment-page-1/>. [Source: Market Watch]

* -i : provide more information about Sean Seah warning rules. Default False.
* -d : print insights into warnings calculation. Default False.

<img width="927" alt="warnings" src="https://user-images.githubusercontent.com/25267873/108609497-2ec03780-73c6-11eb-8577-d5da80dae213.png">

## dp <a name="dp"></a>

```text
usage: dp
```

Display barchart of dark pool (ATS) and OTC (Non ATS) data

![dp](https://user-images.githubusercontent.com/25267873/115130908-7987b580-9feb-11eb-8bca-1999174178d0.png)

## ftd <a name="ftd"></a>

```text
usage: ftd [-s START] [-e END] [-n N_NUM] [--raw] [--export {csv,json,xlsx}]
```

The fails-to-deliver data collected by SEC. Fails to deliver on a given day are a cumulative number of all fails outstanding until that day, plus new fails that occur that day, less fails that settle that day. See <https://www.sec.gov/data/foiadocsfailsdatahtm>. Note that FTD is 1 month delayed. [Source: SEC]

* -n : number of latest fails-to-deliver being printed. Default 0. Overrules start and end FTD datetime. 
* -s : start of datetime to see FTD. Default 20 days in past.
* -e : end of datetime to see FTD. Default today.
* --raw : Print raw data.
* --export : Export dataframe data to csv,json,xlsx file

![ftd](https://user-images.githubusercontent.com/25267873/125202513-d520b280-e26b-11eb-8091-5b221636a5ce.png)


## shortview <a name="shortview"></a>

```text
usage: shortvol [-n NUM] [-r]
```

Shows price vs short interest volume. [Source: Stockgrid]
* -r: Flag to print raw data instead. 
* -n: Number of last open market days to show. Default: 120, but if -r is set it's 10.
* --export: Save dataframe as a csv file. Default: false.

![shortview](https://user-images.githubusercontent.com/25267873/122646172-c4ba6380-d115-11eb-8e5c-6ee3ab70095b.png)

<img width="951" alt="shortvolraw_gme" src="https://user-images.githubusercontent.com/25267873/122323990-eeaa3500-cf1f-11eb-91b9-6b9d3a4eee36.png">


## darkpos <a name="darkpos"></a>

```text
usage: darkpos [-n NUM] [-r]
```

Shows Net Short Vol. vs Position. [Source: Stockgrid]
* -r: Flag to print raw data instead. 
* -n: Number of last open market days to show. Default: 120, but if -r is set it's 10.
* --export: Save dataframe as a csv file. Default: false.

![darkpos](https://user-images.githubusercontent.com/25267873/122646991-f03f4d00-d119-11eb-971f-b554bb4cdec4.png)

<img width="958" alt="darkpos_raw" src="https://user-images.githubusercontent.com/25267873/122646989-ee758980-d119-11eb-9f67-f51f0b75c49d.png">


## supplier <a name="supplier"></a>

```text
usage: supplier
```

List of suppliers from ticker provided. [Source: CSIMarket]

<img width="974" alt="supplier" src="https://user-images.githubusercontent.com/25267873/124523361-b98e5580-ddee-11eb-94dc-08e4df1b17c0.png">


## customer <a name="customer"></a>

```text
usage: customer
```

List of customer from ticker provided. [Source: CSIMarket]

<img width="980" alt="customer" src="https://user-images.githubusercontent.com/25267873/124523360-b85d2880-ddee-11eb-8413-836de13d13ce.png">
