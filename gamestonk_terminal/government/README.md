# GOVERNMENT

This menu aims to get some insights regarding government data, and the usage of the following commands along with an example will be exploited below. 
This data has been provided by [quiverquant](https://www.quiverquant.com).

* [last_congress](#last_congress)
  * last congress trading
* [buy_congress](#buy_congress)
  * top buy congress tickers
* [sell_congress](#sell_congress)
  * top sell congress tickers
* [last_senate](#last_senate)
  * last senate trading
* [buy_senate](#buy_senate)
  * top buy senate tickers
* [sell_senate](#sell_senate)
  * top sell senate tickers
* [last_house](#last_house)
  * last house trading
* [buy_house](#buy_house)
  * top buy house tickers
* [sell_house](#sell_house)
  * top sell house tickers

#### WITH TICKER PROVIDED

* [congress](#congress)
  * congress trades on the ticker
* [senate](#senate)
  * senate trades on the ticker
* [house](#house)
  * house trades on the ticker


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


## congress <a name="congress"></a>
```text
usage: congress [-p PAST_TRANSACTIONS_MONTHS]
```
Congress trading. [Source: www.quiverquant.com]

* -p : Past transaction months. Default: 6.

![congress](https://user-images.githubusercontent.com/25267873/117347548-280f6f80-aea1-11eb-8ee7-b511cdf863e1.png)


## senate <a name="senate"></a>
```text
usage: senate [-p PAST_TRANSACTIONS_MONTHS]
```
Senate trading. [Source: www.quiverquant.com]

* -p : Past transaction months. Default: 6.

![senate](https://user-images.githubusercontent.com/25267873/118394689-187ced00-b63e-11eb-8943-4bd32466ff47.png)


## house <a name="house"></a>
```text
usage: house [-p PAST_TRANSACTIONS_MONTHS]
```
House trading. [Source: www.quiverquant.com]

* -p : Past transaction months. Default: 6.

![house](https://user-images.githubusercontent.com/25267873/118394690-19158380-b63e-11eb-85ba-87fc2fd7df15.png)
