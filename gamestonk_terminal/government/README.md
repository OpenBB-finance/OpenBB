# GOVERNMENT

This menu aims to get some insights regarding government data, and the usage of the following commands along with an example will be exploited below. 
This data has been provided by [quiverquant](https://www.quiverquant.com).

* [last_congress](#last_congress)
  * last congress trading
* [buy_congress](#buy_congress)
  * plot top buy congress tickers
* [sell_congress](#sell_congress)
  * plot top sell congress tickers
* [last_senate](#last_senate)
  * last senate trading
* [buy_senate](#buy_senate)
  * plot top buy senate tickers
* [sell_senate](#sell_senate)
  * plot top sell senate tickers
* [last_house](#last_house)
  * last house trading
* [buy_house](#buy_house)
  * plot top buy house tickers
* [sell_house](#sell_house)
  * plot top sell house tickers
* [last_contracts](#last_contracts)
  * last government contracts
* [sum_contracts](#sum_contracts)
  * plot sum of last government contracts
* [qtr_contracts](#qtr_contracts)
  * quarterly government contracts best regression  
* [top_lobbying](#top_lobbying)
  * top corporate lobbying tickers  

#### WITH TICKER PROVIDED

* [raw_congress](#raw_congress)
  * raw congress trades on the ticker
* [congress](#congress)
  * plot congress trades on the ticker
* [raw_senate](#raw_senate)
  * raw senate trades on the ticke
* [senate](#senate)
  * plot senate trades on the ticker
* [raw_house](#raw_house)
  * raw house trades on the ticker
* [house](#house)
  * plot house trades on the ticker
* [raw_contracts](#raw_contracts)
  * raw contracts on the ticker
* [contracts](#contracts)
  * plot sum of contracts on the ticker
* [qtr_contracts_hist](#qtr_contracts_hist)
  * quarterly government contracts historical
* [lobbying](#lobbying)
  * corporate lobbying details

## last_congress <a name="last_congress"></a>
```text
usage: last_congress [-p PAST_TRANSACTIONS_DAYS]
```
Last congress trading. [Source: www.quiverquant.com]

* -p : Past transaction days. Default: 5.
* -r : Congress representative.

<img width="1013" alt="last_congress" src="https://user-images.githubusercontent.com/25267873/117346752-16799800-aea0-11eb-9b82-c28e712694d1.png">


## buy_congress <a name="buy_congress"></a>
```text
usage: buy_congress [-p PAST_TRANSACTIONS_MONTHS] [-t TOP_NUM]
```
Top buy congress trading. [Source: www.quiverquant.com]

* -p : Past transaction months. Default: 6.
* -t : Number of top tickers. Default: 10.

![buy](https://user-images.githubusercontent.com/25267873/117505803-8b220480-af7c-11eb-91cb-f51d2b585a17.png)


## sell_congress <a name="sell_congress"></a>
```text
usage: sell_congress [-p PAST_TRANSACTIONS_MONTHS] [-t TOP_NUM]
```
Top sell congress trading. [Source: www.quiverquant.com]

* -p : Past transaction months. Default: 6.
* -t : Number of top tickers. Default: 10.

![sold](https://user-images.githubusercontent.com/25267873/117505806-8c533180-af7c-11eb-8223-f11b08c72675.png)


## last_senate <a name="last_senate"></a>
```text
usage: last_senate [-p PAST_TRANSACTIONS_DAYS]
```
Last senate trading. [Source: www.quiverquant.com]

* -p : Past transaction days. Default: 5.
* -r : Congress representative.

<img width="994" alt="last_senate" src="https://user-images.githubusercontent.com/25267873/118394652-c936bc80-b63d-11eb-883d-a1fa690cc6cd.png">


## buy_senate <a name="buy_senate"></a>
```text
usage: buy_senate [-p PAST_TRANSACTIONS_MONTHS] [-t TOP_NUM]
```
Top buy senate trading. [Source: www.quiverquant.com]

* -p : Past transaction months. Default: 6.
* -t : Number of top tickers. Default: 10.

![buy_senate](https://user-images.githubusercontent.com/25267873/118394649-c89e2600-b63d-11eb-8ef2-e33d0e673626.png)


## sell_senate <a name="sell_senate"></a>
```text
usage: sell_senate [-p PAST_TRANSACTIONS_MONTHS] [-t TOP_NUM]
```
Top sell senate trading. [Source: www.quiverquant.com]

* -p : Past transaction months. Default: 6.
* -t : Number of top tickers. Default: 10.

![sell_senate](https://user-images.githubusercontent.com/25267873/118394647-c6d46280-b63d-11eb-9bca-761269fafd68.png)


## last_house <a name="last_house"></a>
```text
usage: last_house [-p PAST_TRANSACTIONS_DAYS]
```
Last house trading. [Source: www.quiverquant.com]

* -p : Past transaction days. Default: 5.
* -r : Congress representative.

<img width="991" alt="last_house" src="https://user-images.githubusercontent.com/25267873/118394650-c936bc80-b63d-11eb-8c9d-f4a3fe4a2aff.png">


## buy_house <a name="buy_house"></a>
```text
usage: buy_house [-p PAST_TRANSACTIONS_MONTHS] [-t TOP_NUM]
```
Top buy house trading. [Source: www.quiverquant.com]

* -p : Past transaction months. Default: 6.
* -t : Number of top tickers. Default: 10.

![buy_house](https://user-images.githubusercontent.com/25267873/118394648-c8058f80-b63d-11eb-99fa-5c1bf00d40b6.png)


## sell_house <a name="sell_house"></a>
```text
usage: sell_house [-p PAST_TRANSACTIONS_MONTHS] [-t TOP_NUM]
```
Top sell house trading. [Source: www.quiverquant.com]

* -p : Past transaction months. Default: 6.
* -t : Number of top tickers. Default: 10.

![sell_house](https://user-images.githubusercontent.com/25267873/118394645-c5a33580-b63d-11eb-8dbe-a9b9d948df24.png)


## last_contracts <a name="last_contracts"></a>
```text
usage: last_contracts [-p PAST_TRANSACTIONS_DAYS] [-l LIMIT_CONTRACTS]
```
Last contracts. [Source: www.quiverquant.com]

* -p : Past transaction months. Default: 2.
* -t : Number of top tickers. Default: 20.

<img width="1081" alt="last_contracts" src="https://user-images.githubusercontent.com/25267873/119065144-d3a5dd00-b9d4-11eb-85c9-ab16255a6996.png">


## sum_contracts <a name="sum_contracts"></a>
```text
usage: sum_contracts
```
Sum latest contracts. [Source: www.quiverquant.com]

![sum_contracts](https://user-images.githubusercontent.com/25267873/119065220-f33d0580-b9d4-11eb-8870-37ca352b187c.png)


## qtr_contracts <a name="qtr_contracts"></a>
```text
usage: qtr_contracts [-t TOP]
```
Quarterly government contracts best regression. [Source: www.quiverquant.com]

![top_promising_stocks](https://user-images.githubusercontent.com/25267873/120394857-f963a800-c32b-11eb-9d3f-2295f7216b67.png)


## top_lobbying <a name="top_lobbying"></a>
```text
usage: top_lobbying [-t TOP]
```
Top lobbying spent. [Source: www.quiverquant.com]

* -t : Top corporate lobbying tickers with biggest amounts. Default 10.

![top_lobbying](https://user-images.githubusercontent.com/25267873/120707733-9e0ff200-c4b2-11eb-9430-552d92f3fc74.png)


#### WITH TICKER PROVIDED 

## raw_congress <a name="raw_congress"></a>
```text
usage: raw_congress [-p PAST_TRANSACTIONS_DAYS]
```
Raw congress trading. [Source: www.quiverquant.com]

* -p : Past transaction days. Default: 10.

<img width="994" alt="raw_congress" src="https://user-images.githubusercontent.com/25267873/118398326-00ae6480-b650-11eb-804e-3194824c3685.png">


## congress <a name="congress"></a>
```text
usage: congress [-p PAST_TRANSACTIONS_MONTHS]
```
Congress trading. [Source: www.quiverquant.com]

* -p : Past transaction months. Default: 6.

![congress](https://user-images.githubusercontent.com/25267873/117347548-280f6f80-aea1-11eb-8ee7-b511cdf863e1.png)


## raw_senate <a name="raw_senate"></a>
```text
usage: raw_senate [-p PAST_TRANSACTIONS_DAYS]
```
Raw senate trading. [Source: www.quiverquant.com]

* -p : Past transaction days. Default: 10.

<img width="990" alt="raw_senate" src="https://user-images.githubusercontent.com/25267873/118398320-f8562980-b64f-11eb-9ad9-c64c12f9a3cf.png">


## senate <a name="senate"></a>
```text
usage: senate [-p PAST_TRANSACTIONS_MONTHS]
```
Senate trading. [Source: www.quiverquant.com]

* -p : Past transaction months. Default: 6.

![senate](https://user-images.githubusercontent.com/25267873/118394689-187ced00-b63e-11eb-8943-4bd32466ff47.png)


## raw_house <a name="raw_house"></a>
```text
usage: raw_house [-p PAST_TRANSACTIONS_DAYS]
```
Raw house trading. [Source: www.quiverquant.com]

* -p : Past transaction days. Default: 10.

<img width="990" alt="raw_house" src="https://user-images.githubusercontent.com/25267873/118398317-f68c6600-b64f-11eb-898a-1d1d46c8f5c3.png">


## house <a name="house"></a>
```text
usage: house [-p PAST_TRANSACTIONS_MONTHS]
```
House trading. [Source: www.quiverquant.com]

* -p : Past transaction months. Default: 6.

![house](https://user-images.githubusercontent.com/25267873/118394690-19158380-b63e-11eb-85ba-87fc2fd7df15.png)


## raw_contracts <a name="raw_contracts"></a>
```text
usage: raw_contracts [-p PAST_TRANSACTIONS_DAYS]
```
Raw contracts. [Source: www.quiverquant.com]

* -p : Past transaction months. Default: 10.

<img width="1109" alt="raw_contracts" src="https://user-images.githubusercontent.com/25267873/119065403-59298d00-b9d5-11eb-832c-3dd85d66bee1.png">


## contracts <a name="contracts"></a>
```text
usage: contracts [-p PAST_TRANSACTIONS_DAYS]
```
Contracts associated with ticker. [Source: www.quiverquant.com]

* -p : Past transaction months. Default: 10.

![contracts](https://user-images.githubusercontent.com/25267873/119065405-59c22380-b9d5-11eb-9a34-9cad288b22de.png)


## qtr_contracts_hist <a name="qtr_contracts_hist"></a>
```text
usage: qtr_contracts_hist
```
Quarterly government contracts historical. [Source: www.quiverquant.com]

![qtr_contracts_hist](https://user-images.githubusercontent.com/25267873/120394929-113b2c00-c32c-11eb-8241-78d5d1328386.png)


## lobbying <a name="lobbying"></a>
```text
usage: lobbying [-l LAST]
```
Lobbying details. [Source: www.quiverquant.com]

* -l : Last corporate lobbying details. Default: 10.

<img width="1222" alt="Captura de ecrã 2021-06-03, às 21 25 02" src="https://user-images.githubusercontent.com/25267873/120707931-d1528100-c4b2-11eb-9619-82c896aaa9e7.png">

