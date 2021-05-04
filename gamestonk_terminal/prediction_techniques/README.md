# PREDICTION TECHNIQUES

This menu aims to predict the share price of a pre-loaded stock, and the usage of the following commands along with an example will be exploited below. See [How to fune-tuning a NN model](FUNE-TUNING-NN-models.md).

  * [sma](#sma)
    - simple moving average
  * [ets](#ets)
    - Exponential Smoothing (e.g. Holt-Winters)
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
    - Contains a [looping example](#looping)
  * [lstm](#lstm)
    - Long-Short Term Memory
    - Contains a [backtesting example](#backtesting)

**Note:** _Use this at your own discretion. All of these prediciton techniques rely solely on the closing price of the stock. This means that there are several factors that the models aren't aware of at the time of prediction, and may - drastically - move the price up or down. Examples are: news, analyst price targets, reddit post, tweets from Elon Musk, and so on._

**Note 2:** _[Enabling GPU acceleration for TensorFlow requires CUDA setup](README-gpu-accel.md) and will probably not provide any speedup unless you are building large custom models._



## sma <a name="sma"></a>
```
usage: sma [-l N_LENGTH] [-d N_DAYS]
```
Simple Moving Average:
  * -l : length of SMA window. Default 20.
  * -d : prediciton days. Default 5.
  * -e : end date (format YYYY-MM-DD) of the stock - Backtesting. Default None.

![sma](https://user-images.githubusercontent.com/25267873/108604945-d29aea80-73a8-11eb-8dac-6a545b9c52b9.png)

## ets <a name="ets"></a>
```
usage: ets [-t TREND] [-s SEASONAL] [-p SEASONAL_PERIODS] [-d N_DAYS]
```
Exponential Smoothing (based on trend+seasonality, see https://otexts.com/fpp2/taxonomy.html):
  * -t : trend component: N: None, A: Additive, Ad: Additive Damped. Default N.
  * -s : seasonality component: N: None, A: Additive, M: Multiplicative. Default N.
  * -p : seasonal periods. Default 5.
  * -d : prediciton days. Default 5.
  * -e : end date (format YYYY-MM-DD) of the stock - Backtesting. Default None.

![ets_pltr](https://user-images.githubusercontent.com/25267873/110266847-97a6d280-7fb6-11eb-997e-0b598abc713b.png)

## knn <a name="knn"></a>
```
usage: knn [-i N_INPUTS] [-d N_DAYS] [-j N_JUMPS] [-n N_NEIGHBORS]
```
k-Nearest Neighbors:
  * -i : number of days to use for prediction. Default 40.
  * -d : prediciton days. Default 5.
  * -j : number of jumps in training data. Default 1.
  * -n : number of neighbors to use on the algorithm. Default 20.
  * -e : end date (format YYYY-MM-DD) of the stock - Backtesting. Default None.

![knn](https://user-images.githubusercontent.com/25267873/108604942-d169bd80-73a8-11eb-9021-6f787cbd41e3.png)

## linear <a name="linear"></a>
```
usage: linear [-i N_INPUTS] [-d N_DAYS] [-j N_JUMPS]
usage: regression -p 1 [-i N_INPUTS] [-d N_DAYS] [-j N_JUMPS]
```
Linear Regression (p=1):
  * -i : number of days to use for prediction. Default 40.
  * -d : prediciton days. Default 5.
  * -j : number of jumps in training data. Default 1.
  * -e : end date (format YYYY-MM-DD) of the stock - Backtesting. Default None.

![linear](https://user-images.githubusercontent.com/25267873/108604948-d3cc1780-73a8-11eb-860f-49274a34038b.png)

## quadratic <a name="quadratic"></a>
```
usage: quadratic [-i N_INPUTS] [-d N_DAYS] [-j N_JUMPS]
usage: regression -p 2 [-i N_INPUTS] [-d N_DAYS] [-j N_JUMPS]
```
Quadratic Regression (p=2):
  * -i : number of days to use for prediction. Default 40.
  * -d : prediciton days. Default 5.
  * -j : number of jumps in training data. Default 1.
  * -e : end date (format YYYY-MM-DD) of the stock - Backtesting. Default None.

![quadratic](https://user-images.githubusercontent.com/25267873/108604935-cca50980-73a8-11eb-9af1-bba807203cc6.png)

## cubic <a name="cubic"></a>
```
usage: cubic [-i N_INPUTS] [-d N_DAYS] [-j N_JUMPS]
usage: regression -p 3 [-i N_INPUTS] [-d N_DAYS] [-j N_JUMPS]
```
Cubic Regression (p=3):
  * -i : number of days to use for prediction. Default 40.
  * -d : prediciton days. Default 5.
  * -j : number of jumps in training data. Default 1.
  * -e : end date (format YYYY-MM-DD) of the stock - Backtesting. Default None.

![cubic](https://user-images.githubusercontent.com/25267873/108604941-d169bd80-73a8-11eb-9220-84a7013e1283.png)

## regression <a name="regression"></a>
```
usage: regression -p N_POLYNOMIAL [-i N_INPUTS] [-d N_DAYS] [-j N_JUMPS]
```
Regression:
  * -i : number of days to use for prediction. Default 40.
  * -d : prediciton days. Default 5.
  * -j : number of jumps in training data. Default 1.
  * -p : polynomial associated with regression. Required.
  * -e : end date (format YYYY-MM-DD) of the stock - Backtesting. Default None.

![regression](https://user-images.githubusercontent.com/25267873/108604946-d3338100-73a8-11eb-9e99-fa526fb56672.png)

## arima <a name="arima"></a>
```
usage: arima [-d N_DAYS] [-i {aic,aicc,bic,hqic,oob}] [-s] [-r] [-o S_ORDER]
```
Auto-Regressive Integrated Moving Average:
  * -d : prediciton days. Default 5.
  * -i : information criteria - used if auto_arima library is invoked. Default aic.
  * -s : weekly seasonality flag. Default False.
  * -r : results about ARIMA summary flag. Default False.
  * -o : arima model order. If the model order is defined, auto_arima is not invoked, deeming information criteria useless. <br />Example: `-o 5,1,4` where:
    * p = 5 : order (number of time lags) of the autoregressive model.
    * d = 1 : degree of differencing (the number of times the data have had past values subtracted).
    * q = 4 : order of the moving-average model.
  * -e : end date (format YYYY-MM-DD) of the stock - Backtesting. Default None.

![arima](https://user-images.githubusercontent.com/25267873/108604947-d3cc1780-73a8-11eb-9dbb-53b959ae7947.png)

## prophet <a name="prophet"></a>
```
usage: fbprophet [-d N_DAYS]
```
Facebook's Prophet:
  * -d : prediciton days. Default 5.
  * -e : end date (format YYYY-MM-DD) of the stock - Backtesting. Default None.

![prophet](https://user-images.githubusercontent.com/25267873/108604938-cf9ffa00-73a8-11eb-973b-0affb343e2f6.png)

## mlp <a name="mlp"></a>
```
usage: mlp [-d N_DAYS] [-i N_INPUTS] [-j N_JUMPS] [--epochs N_EPOCHS] [-p {normalization,standardization,none}]
[-o {adam,adagrad,adadelta,adamax,ftrl,nadam,optimizer,rmsprop,sgd}] [-l {mae,mape,mse,msle}] [-e S_END_DATE] [--loops N_LOOPS]
```
MulitLayer Perceptron:
  * -d : prediciton days. Default 5.
  * -i : number of days to use for prediction. Default 40.
  * -j : number of jumps in training data. Default 1.
  * --epochs : number of training epochs. Default 200.
  * -p : pre-processing data. Default normalization.
  * -o : optimization technique. Default adam.
  * -l : loss function. Default mae.
  * -e : end date (format YYYY-MM-DD) of the stock - Backtesting. Default None.
  * --xla_cpu: if present, will enable XLA for CPU (overrides environment variables during run).
  * --xla_gpu: if present, will enable XLA for GPU (overrides environment variables during run).
  * --force_allow_gpu_growth: if true, will force TensorFlow to allow GPU memory usage to grow as needed. Otherwise will allocate 100% of available GPU memory when CUDA is set up. Default true.
  * --batch_size: batch size for model training, should not be used unless advanced user. Default None.
  * --loops: number of loops to iterate and train models. Default 1.

Due to the complexity of defining a model through command line, one can define it in: [config_neural_network_models.txt](/config_neural_network_models.py)
```
MultiLayer_Perceptron \
    = [ {'Dense':
                {'units':50, 'activation':'relu'} },
        {'Dense':
                {'units':100, 'activation':'relu'} },
        {'Dense':
                {'units':80, 'activation':'relu'} },
        {'Dense':
                {'units':30, 'activation':'relu'} },
        {'Dense':
                {'activation':'linear'} }]
```

![mlp](https://user-images.githubusercontent.com/25267873/108604944-d2025400-73a8-11eb-9ab6-52972160cd2a.png)

## rnn <a name="rnn"></a>
```
usage: rnn [-d N_DAYS] [-i N_INPUTS] [-j N_JUMPS] [--epochs N_EPOCHS] [-p {normalization,standardization,none}]
[-o {adam,adagrad,adadelta,adamax,ftrl,nadam,optimizer,rmsprop,sgd}] [-l {mae,mape,mse,msle}] [-e S_END_DATE] [--loops N_LOOPS]
```
Recurrent Neural Network:
  * -d : prediciton days. Default 5.
  * -i : number of days to use for prediction. Default 40.
  * -j : number of jumps in training data. Default 1.
  * --epochs : number of training epochs. Default 200.
  * -p : pre-processing data. Default normalization.
  * -o : optimization technique. Default adam.
  * -l : loss function. Default mae.
  * -e : end date (format YYYY-MM-DD) of the stock - Backtesting. Default None.
  * --xla_cpu: if present, will enable XLA for CPU (overrides environment variables during run).
  * --xla_gpu: if present, will enable XLA for GPU (overrides environment variables during run).
  * --force_allow_gpu_growth: if true, will force TensorFlow to allow GPU memory usage to grow as needed. Otherwise will allocate 100% of available GPU memory when CUDA is set up. Default true.
  * --batch_size: batch size for model training, should not be used unless advanced user. Default None.
  * --loops: number of loops to iterate and train models. Default 1.

Due to the complexity of defining a model through command line, one can define it in: [config_neural_network_models.txt](/config_neural_network_models.py)
```
Recurrent_Neural_Network \
    = [ {'SimpleRNN':
                {'units':100, 'activation':'linear', 'return_sequences':True} },
        {'SimpleRNN':
                {'units':50, 'activation':'linear', 'return_sequences':True} },
        {'Dropout':
                {'rate':0.2} },
        {'SimpleRNN':
                {'units':21, 'activation':'linear', 'return_sequences':False} },
        {'Dense':
                {'activation':'linear'} }]
```

![rnn](https://user-images.githubusercontent.com/25267873/108604940-d0d12700-73a8-11eb-837e-a5aa128942d9.png)

### Looping Example <a name="looping"></a>

![loops](https://user-images.githubusercontent.com/25267873/111932423-479b3600-8ab5-11eb-9d0b-7210d5f02e83.png)

<img width="1006" alt="Captura de ecrã 2021-03-22, às 02 14 38" src="https://user-images.githubusercontent.com/25267873/111932420-436f1880-8ab5-11eb-831c-ebb88f1c5473.png">


## lstm <a name="lstm"></a>
```
usage: lstm [-d N_DAYS] [-i N_INPUTS] [-j N_JUMPS] [--epochs N_EPOCHS] [-p {normalization,standardization,none}]
[-o {adam,adagrad,adadelta,adamax,ftrl,nadam,optimizer,rmsprop,sgd}] [-l {mae,mape,mse,msle}] [-e S_END_DATE] [--loops N_LOOPS]
```
Long-Short Term Memory:
  * -d : prediciton days. Default 5.
  * -i : number of days to use for prediction. Default 40.
  * -j : number of jumps in training data. Default 1.
  * --epochs : number of training epochs. Default 200.
  * -p : pre-processing data. Default normalization.
  * -o : optimization technique. Default adam.
  * -l : loss function. Default mae.
  * -e : end date (format YYYY-MM-DD) of the stock - Backtesting. Default None.
  * --xla_cpu: if present, will enable XLA for CPU (overrides environment variables during run).
  * --xla_gpu: if present, will enable XLA for GPU (overrides environment variables during run).
  * --force_allow_gpu_growth: if true, will force TensorFlow to allow GPU memory usage to grow as needed. Otherwise will allocate 100% of available GPU memory when CUDA is set up. Default true.
  * --batch_size: batch size for model training, should not be used unless advanced user. Default None.
  * --loops: number of loops to iterate and train models. Default 1.

Due to the complexity of defining a model through command line, one can define it in: [config_neural_network_models.py](/config_neural_network_models.py)
```
Long_Short_Term_Memory \
    = [ {'LSTM':
                {'units':25, 'activation':'tanh', 'return_sequences':True} },
        {'LSTM':
                {'units':15, 'activation':'tanh', 'return_sequences':False} },
        {'Dense':
                {'activation':'linear'} }]
```

![lstm](https://user-images.githubusercontent.com/25267873/108604943-d2025400-73a8-11eb-83c5-edb4a2121cba.png)

### Backtesting Example <a name="backtesting"></a>

![appl_pred](https://user-images.githubusercontent.com/25267873/111053156-4173dc80-8459-11eb-9fcb-e81211961743.png)

![apple_error](https://user-images.githubusercontent.com/25267873/111053157-420c7300-8459-11eb-8c37-fb1b5208d635.png)

<img width="992" alt="Captura de ecrã 2021-03-14, às 00 06 51" src="https://user-images.githubusercontent.com/25267873/111053158-420c7300-8459-11eb-993b-6d9c26f98af9.png">

