# PREDICTION TECHNIQUES

This menu aims to predict the share price of a pre-loaded stock, and the usage of the following commands along with an example will be exploited below.

  * [sma](#sma)
    - simple moving average
  * [knn](#knn)
    - k-Nearest Neighbors
  * [linear](#linear)
    - linear regression (polynomial 1)
  * [quadratic](#quadratic)
    - quadratic regression (polynomial 2)
  * [cubic](#cubic)
    - cubic regression (polynomial 3)
  * [regression](#regression)
    - regression (other polynomial)
  * [arima](#arima)
    - autoregressive integrated moving average
  * [prophet](#prophet)
    - Facebook's prophet prediction
  * [mlp](#mlp)
    - MultiLayer Perceptron
  * [rnn](#rnn)
    - Recurrent Neural Network
  * [lstm](#lstm)
    - Long-Short Term Memory

**Note:** _Use this at your own discretion. All of these prediciton techniques rely solely on the closing price of the stock. This means that there are several factors that the models aren't aware of at the time of prediction, and may - drastically - move the price up or down. Examples are: news, analyst price targets, reddit post, tweets from Elon Musk, and so on._


## sma <a name="sma"></a>
```
usage: simple_moving_average [-l N_LENGTH] [-d N_DAYS]
```
  * -l : length of SMA window. Default 20.
  * -d : prediciton days. Default 5.

![sma](https://user-images.githubusercontent.com/25267873/108604945-d29aea80-73a8-11eb-8dac-6a545b9c52b9.png)

## knn <a name="knn"></a>
```
usage: knn [-i N_INPUTS] [-d N_DAYS] [-j N_JUMPS] [-n N_NEIGHBORS]
```
  * -i : number of days to use for prediction. Default 40.
  * -d : prediciton days. Default 5.
  * -j : number of jumps in training data. Default 1.
  * -n : number of neighbors to use on the algorithm. Default 20.

![knn](https://user-images.githubusercontent.com/25267873/108604942-d169bd80-73a8-11eb-9021-6f787cbd41e3.png)

## linear <a name="linear"></a>
```
usage: linear [-i N_INPUTS] [-d N_DAYS] [-j N_JUMPS]
usage: regression -p 1 [-i N_INPUTS] [-d N_DAYS] [-j N_JUMPS]
```
  * -i : number of days to use for prediction. Default 40.
  * -d : prediciton days. Default 5.
  * -j : number of jumps in training data. Default 1.

![linear](https://user-images.githubusercontent.com/25267873/108604948-d3cc1780-73a8-11eb-860f-49274a34038b.png)

## quadratic <a name="quadratic"></a>
```
usage: quadratic [-i N_INPUTS] [-d N_DAYS] [-j N_JUMPS]
usage: regression -p 2 [-i N_INPUTS] [-d N_DAYS] [-j N_JUMPS]
```
  * -i : number of days to use for prediction. Default 40.
  * -d : prediciton days. Default 5.
  * -j : number of jumps in training data. Default 1.

![quadratic](https://user-images.githubusercontent.com/25267873/108604935-cca50980-73a8-11eb-9af1-bba807203cc6.png)

## cubic <a name="cubic"></a>
```
usage: cubic [-i N_INPUTS] [-d N_DAYS] [-j N_JUMPS]
usage: regression -p 3 [-i N_INPUTS] [-d N_DAYS] [-j N_JUMPS]
```
  * -i : number of days to use for prediction. Default 40.
  * -d : prediciton days. Default 5.
  * -j : number of jumps in training data. Default 1.

![cubic](https://user-images.githubusercontent.com/25267873/108604941-d169bd80-73a8-11eb-9220-84a7013e1283.png)

## regression <a name="regression"></a>
```
usage: regression -p N_POLYNOMIAL [-i N_INPUTS] [-d N_DAYS] [-j N_JUMPS]
```
  * -i : number of days to use for prediction. Default 40.
  * -d : prediciton days. Default 5.
  * -j : number of jumps in training data. Default 1.
  * -p : polynomial associated with regression. Required.

![regression](https://user-images.githubusercontent.com/25267873/108604946-d3338100-73a8-11eb-9e99-fa526fb56672.png)

## arima <a name="arima"></a>

![arima](https://user-images.githubusercontent.com/25267873/108604947-d3cc1780-73a8-11eb-9dbb-53b959ae7947.png)

## prophet <a name="prophet"></a>

![prophet](https://user-images.githubusercontent.com/25267873/108604938-cf9ffa00-73a8-11eb-973b-0affb343e2f6.png)

## mlp <a name="mlp"></a>

![mlp](https://user-images.githubusercontent.com/25267873/108604944-d2025400-73a8-11eb-9ab6-52972160cd2a.png)

## rnn <a name="rnn"></a>

![rnn](https://user-images.githubusercontent.com/25267873/108604940-d0d12700-73a8-11eb-837e-a5aa128942d9.png)

## lstm <a name="lstm"></a>

![lstm](https://user-images.githubusercontent.com/25267873/108604943-d2025400-73a8-11eb-83c5-edb4a2121cba.png)


