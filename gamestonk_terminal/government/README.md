# GOVERNMENT

This menu aims to get some insights regarding government data, and the usage of the following commands along with an example will be exploited below. 
This data has been provided by [quiverquant](https://www.quiverquant.com).

* [last_congress](#last_congress)
  * last congress trading
* [buy_congress](#buy_congress)
  * top buy congress tickers
* [sell_congress](#sell_congress)
  * top sell congress tickers

#### WITH TICKER PROVIDED

* [congress](#congress)
  * congress trades on the ticker


## last_congress <a name="last_congress"></a>
```text
usage: last_congress [-p PAST_TRANSACTIONS_DAYS]
```
Last congress trading. [Source: www.quiverquant.com]

* -p : Past transaction days. Default: 3.

<img width="1013" alt="last_congress" src="https://user-images.githubusercontent.com/25267873/117346752-16799800-aea0-11eb-9b82-c28e712694d1.png">


## buy_congress <a name="buy_congress"></a>
```text
usage: buy_congress [-p PAST_TRANSACTIONS_MONTHS] [-t TOP_NUM]
```
Top buy congress trading. [Source: www.quiverquant.com]

* -p : Past transaction months. Default: 6.
* -t : Number of top tickers. Default: 10.

<img width="1006" alt="buy_congress" src="https://user-images.githubusercontent.com/25267873/117346660-f4801580-ae9f-11eb-845b-7d403bffacc6.png">


## sell_congress <a name="sell_congress"></a>
```text
usage: sell_congress [-p PAST_TRANSACTIONS_MONTHS] [-t TOP_NUM]
```
Top sell congress trading. [Source: www.quiverquant.com]

* -p : Past transaction months. Default: 6.
* -t : Number of top tickers. Default: 10.

<img width="1010" alt="sell_congress" src="https://user-images.githubusercontent.com/25267873/117346669-f77b0600-ae9f-11eb-8d81-7aa366c596b3.png">


## congress <a name="congress"></a>
```text
usage: congress [-p PAST_TRANSACTIONS_MONTHS]
```
Congress trading. [Source: www.quiverquant.com]

* -p : Past transaction months. Default: 6.

![congress](https://user-images.githubusercontent.com/25267873/117347548-280f6f80-aea1-11eb-8ee7-b511cdf863e1.png)

