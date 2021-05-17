# Validate/Tweaking Neural Network Model

Note: Modeling a NN this way is intended for learning purposes (or fun) only. A user guess or YOLOing on GME may present better returns - No financial advisor tho.

1. **Select the stock that you want to attempt to predict share price**
```
load MSFT
```

2. **Slice the stock price to only relevant data**

Look at the overall share price and try to understand from when does it start behaving similarly. E.g. looking at MSFT, for me, it starts behaving similarly after 2014. Before that, the stock price is rather flat, and not representative of the current pattern.
```
load MSFT -s 2014-01-01
```

3. **Out of this training data, select which part will be used for validation**

Anyone reading this, note this is quite a discussion between the devs.  Since this is a time series, there is an inherent
ordering of the data.  However, since returns are random, it is hard to predict, and ordering data may not have any meaning.

To this end, we allow users to specify how much validation data to use and if it should be shuffled.  By default, we will split 
into 10% validation data with a random shuffle.  This will allow the user to see how the model performs at various times in your sequence.

```
-v/--valid : validation split of data.  Default 0.1 (10%)
--no_shuffle : Flag that will order the validation data so that the last (-v) percent of data is the validation.
```
To try "backtesting" to a certain data, you can specify the end date.  This will forecast and compare the true data from that time.
```
-e/--end : end date (format YYYY-MM-DD) of the stock - Backtesting. Default None.
```

4. **Pre-processing data**

Decide whether you want to pre-process your share price data or not. I.e. do you want to use these values between 18 and 245, or perhaps normalize these between 0 and 1? The later may improve performance.
```
Preprocess = "minmax"
```
This is defined in the config file.

5. **Select input, prediction days and jumps in training data**

The **input** corresponds to the number of days that our model will use for prediction.

The more past days, the more information our model will have to make a sensible prediction. However, the more days being used will lead to a model that takes longer to train, and some days in the past may have no affect in the prediction. In order to facilitate this decision, think of it in terms of months, e.g. 40 days corresponds to roughly 2 months of data. If you think that the share price today can impact the value that it will take in 2 months, then 40 is a good value, otherwise pick a shorter value.
```
-i/--input : number of days to use for prediction. Default 40.
```

The **prediction days** is the number we want to predict for.

Personally, I recommend to set this for a really short window. This is because the bigger the window, the less reliable the prediction is. This is mainly due to the fact that by having a larger prediction horizon, more unexpected events (news, insider trading activity, rumours, ...) can occur, which may shift share price.
```
-d/--days : prediciton days. Default 5.
```

6. **Select NN architecture.** TL;DR: LSTM > RNN > MLP

**MLP**: The neurons don't have any memory.
**RNN***: The neurons can only retain really recent memory.
**LSTM** (improved RNN): The neurons have a long-term memory, hence why this is used for text prediction, since the beginning of a sentence is important to predict the ending.

Have a look at: https://colah.github.io/posts/2015-08-Understanding-LSTMs/

7. **Define NN Model**

**Number of hidden layers**: Due to the complexity of these NN models (particularly LSTM), this value should be kept low (2, 3 or 4). Otherwise, the model will not generalize well to unseen examples (i.e. it will overfit).

**Number of units per layers**: This is one of the hardest to know how to set, I usually set this one by trial and iteration, and understanding how the model performs. Note: Be carefully about this iterative process, to not overfit your hyperparameters to work well in the validation data. Because then it may fail badly on the real prediction.

**Activation function**: _tanh_ is recommended. It is proved to outperform other activation functions. See https://stats.stackexchange.com/questions/101560/tanh-activation-function-vs-sigmoid-activation-function

**Dropout layer**: As a rule of thumb, an LSTM layer should be followed by a Dropout layer with a 20% rate. This is in order to prevent overfitting, while keeping model accuracy.

**Dense layer**: Dense layer to represent outputs.

```
Long_Short_Term_Memory \
    = [ {'LSTM':
                {'units':25, 'activation':'tanh', 'return_sequences':True} },
        {"Dropout":
                {"rate": 0.2} },
        {'LSTM':
                {'units':15, 'activation':'tanh', 'return_sequences':False} },
        {'Dense':
                {'activation':'linear'} }]
```
This model is set in [config_neural_network_models.py](/config_neural_network_models.py)

8. **Model compilation with loss function and optimization technique**

**Loss function**: Often chosen having the activation functions of the hidden layers in mind. See https://machinelearningmastery.com/how-to-choose-loss-functions-when-training-deep-learning-neural-networks/, and https://www.tensorflow.org/api_docs/python/tf/keras/losses.
```
Loss = "mae"
```
This is defined in the config file.

**Optimizer technique**:Adaptive Moment Estimation (_adam_) is usually the default choice for this type of problems. See https://www.tensorflow.org/api_docs/python/tf/keras/optimizers.

The optimizer selection has been moved to the config_neural_network_models.py file and the new argument is the learning rate.
This tells your model how "fast" to train by adjusting the factor that gets multiplied to the loss function for updating weights
```
--lr : learning rate. Default 0.01.
```

9. **Training epochs**

Select the number of epochs to train your model. The bigger number of epochs, the longer the training will take, and also increase chances of overfitting.

An early stopping has been implemented that will (if desired) stop training once the validation loss has plateaued.  the patience (number of 
epochs with no improvement) can be found in the config file.
```
--epochs : number of training epochs. Default 200.
```

10. **Model training loops**

Select the number of loops to - using the defined model - train and predict. This allows to build confidence on the model you are building, and understand what's the median results and also the lower and upper quantiles, of 10 and 90%, respectively.
```
--loops: number of loops to iterate and train models. Default 1.
```

11. **Interpret accuracy metrics**

Interpret the following metrics: MAPE, R2, MAE, MSE and RMSE.

12. **Advanced User**
```
--batch_size: batch size for model training, should not be used unless advanced user. Default None.
```
This can be set to `floor(log2(input_layer_size))` for much faster training if a large amount of input samples (assuming you have the RAM for it). It shouldn't have much effect on the results.

```
--xla_cpu: if present, will enable XLA for CPU (overrides environment variables during run).
--xla_gpu: if present, will enable XLA for GPU (overrides environment variables during run).
--force_allow_gpu_growth: if true, will force TensorFlow to allow GPU memory usage to grow as needed. Otherwise will allocate 100% of available GPU memory when CUDA is set up. Default true.
```
See https://www.tensorflow.org/xla

In the Roadmap: Cross-Validation (Forward Chaining, K-Fold, Group K-fold), NN to use sentiment analysis
