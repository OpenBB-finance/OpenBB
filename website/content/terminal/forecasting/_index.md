---
title: Introduction to Forecast
keywords: "machine learning, statistics, deep learning, neural networks, time series, research, feature engineering, hyperparameters"
excerpt: "The introduction to Forecast explains how to use the menu"
geekdocCollapseSection: true
---

The forecasting menu is a machine learning toolkit that provides practitioners with high-level components that can quickly provide state-of-the-art results, be it with with classical or deep learning models, while also providing researchers with low-level components that can be mixed, matched and fine tuned to build new approaches and custom tuned models. Bring in multiple datasets and train machine learning models with unlimited external factors to see how underlying data may change future forecasting predictions and accuracy. 

## Accessing the Forecast menu

The Forecast menu is called upon by typing `forecast` which opens the following menu:
```
(🦋) / $ forecast
```
<img width="1084" alt="image" src="https://user-images.githubusercontent.com/105685594/189725952-e3feb360-0391-4e05-a51b-4ee678af058a.png">

## How to Use

To begin any machine learning, you must first load in data. The menu supports importing both terminal datasets found in `stocks` and `cryptocurrency`, along with external datasets in the form of `.csv` that can be placed in the following location: `.../OpenBBTerminal/custom_imports/forecast/`

It is important to note, if you ever have troubles on running a command, please read the help commands to guide you on what is available. You can do this by trailing any command with a `-h`

```
(🦋) /forecast/ $ <command> -h
```

### Loading Data

Importing data from within the terminal can be simply done as follows:

```
(🦋) / $ stocks
(🦋) /stocks/ $ load AAPL
(🦋) /stocks/ $ forecast
```
The menu can support loading in unlimited datasets. Once the first one is loaded, the menu options should turn blue to allow you to begin working through the menu options.

To load external data in the form as `.csv`, please place them into the folder shown within your terminal menu and then load them in as follows:

```
(🦋) / $ forecast
(🦋) /forecast/ $ load msft.csv
```
<img width="1091" alt="image" src="https://user-images.githubusercontent.com/105685594/189728980-06ea171a-f088-4bd5-8849-2eadde984ad6.png">

### Understanding the structure of the menu 

The menu is broken up into three distinct sections. These sections represent the typical order of operations a machine learning professional would have to take in order to complete a project. 

Once data is loaded in, begin with `Exploration`.

`Exploration`: Explore the datasets loaded into the menu to further understand your data and create unique new datasets by combining and analyzing features. Functions to note: `plot`, `combine`, `desc`, `corr`
<img width="692" alt="image" src="https://user-images.githubusercontent.com/105685594/189729792-079f151e-f2b4-41bf-99d9-c83849c59170.png">


`Feature Engineering`: Manuipulate datasets (addition, deletion, combination, mutation) of your data set to potentially improve machine learning model training, by providing new features and covariates that may leading to better performance and greater accuracy.
<img width="694" alt="image" src="https://user-images.githubusercontent.com/105685594/189730399-fc4051f2-4d8e-4ff1-8494-44528d8f5513.png">


`TimeSeries Forecasting`: Train state of the art models on custom datasets and experiment tuning hyperparameters. For more information on specific model implementations, please see [Darts Models](https://unit8co.github.io/darts/generated_api/darts.models.forecasting.html) for in depth documentation. 
<img width="694" alt="image" src="https://user-images.githubusercontent.com/105685594/189730287-1c5c8141-1801-4a35-b9e9-acb32be35c13.png">


## Sample workflow (beginner) 

Let's begin by using one of the datasets we loaded in previously : `AAPL`

We will be forecasting `5 Business days` ahead for the remaider of these workflows unless specified. 

Note: All models automatically perform Historical backtesting on the test split before providing a prediction.

Note: `MAPE` = mean average precision error.

```
(🦋) /forecast/ $ plot AAPL.close
```
<img width="792" alt="image" src="https://user-images.githubusercontent.com/105685594/189739347-476b24d5-ee68-43ac-9fad-e780f64ab72f.png">

```
(🦋) /forecast/ $ desc AAPL

            Showing Descriptive Statistics for Dataset AAPL             
┏━━━━━━━┳━━━━━━━━┳━━━━━━━━┳━━━━━━━━┳━━━━━━━━┳━━━━━━━━━━━┳━━━━━━━━━━━━━━┓
┃       ┃ open   ┃ high   ┃ low    ┃ close  ┃ adj_close ┃ volume       ┃
┡━━━━━━━╇━━━━━━━━╇━━━━━━━━╇━━━━━━━━╇━━━━━━━━╇━━━━━━━━━━━╇━━━━━━━━━━━━━━┩
│ count │ 758.00 │ 758.00 │ 758.00 │ 758.00 │ 758.00    │ 758.00       │
├───────┼────────┼────────┼────────┼────────┼───────────┼──────────────┤
│ mean  │ 121.57 │ 123.07 │ 120.15 │ 121.68 │ 120.72    │ 113864153.69 │
├───────┼────────┼────────┼────────┼────────┼───────────┼──────────────┤
│ std   │ 36.37  │ 36.74  │ 35.95  │ 36.34  │ 36.61     │ 56098731.72  │
├───────┼────────┼────────┼────────┼────────┼───────────┼──────────────┤
│ min   │ 53.47  │ 54.11  │ 52.77  │ 53.54  │ 52.38     │ 41000000.00  │
├───────┼────────┼────────┼────────┼────────┼───────────┼──────────────┤
│ 25%   │ 83.10  │ 86.41  │ 83.04  │ 84.16  │ 83.00     │ 77032650.00  │
├───────┼────────┼────────┼────────┼────────┼───────────┼──────────────┤
│ 50%   │ 128.18 │ 129.64 │ 126.63 │ 127.86 │ 126.70    │ 98135650.00  │
├───────┼────────┼────────┼────────┼────────┼───────────┼──────────────┤
│ 75%   │ 149.05 │ 150.38 │ 147.69 │ 149.14 │ 148.50    │ 131152875.00 │
├───────┼────────┼────────┼────────┼────────┼───────────┼──────────────┤
│ max   │ 182.63 │ 182.94 │ 179.12 │ 182.01 │ 181.26    │ 426510000.00 │
└───────┴────────┴────────┴────────┴────────┴───────────┴──────────────┘
```

Let's use a simple **Probabilistic Exponential Smoothing Model** to predict the close price. Keep in mind all models are perform automatic histoical backtesting before providing future forecasts. 

Note: All models forecaste `close` by default.

```
(🦋) /forecast/ $ expo AAPL

100%|███████████████████████████████████████████████████████████████████████████████████████████████████████████████████| 115/115 [00:17<00:00,  6.44it/s]
Exponential smoothing obtains MAPE: 3.86% 


   Actual price: 157.37    
┏━━━━━━━━━━━━┳━━━━━━━━━━━━┓
┃ Datetime   ┃ Prediction ┃
┡━━━━━━━━━━━━╇━━━━━━━━━━━━┩
│ 2022-09-12 │ 157.99     │
├────────────┼────────────┤
│ 2022-09-13 │ 157.89     │
├────────────┼────────────┤
│ 2022-09-14 │ 158.32     │
├────────────┼────────────┤
│ 2022-09-15 │ 158.25     │
├────────────┼────────────┤
│ 2022-09-16 │ 158.52     │
└────────────┴────────────┘
```
<img width="792" alt="image" src="https://user-images.githubusercontent.com/105685594/189740925-ed0fb214-8b1c-4aff-a149-517d122082c8.png">

That looks great, but we might want to see it a little more up close. Lets set the flag for `--forecast-only`.

<img width="791" alt="image" src="https://user-images.githubusercontent.com/105685594/189741811-21832a87-f05f-4191-88f8-6ac30eb3d7b6.png">


We can also play with some models that are bit more advanced. As we go down the list, models begin to become larger in parameter size and complexity. This will play a key role later on when we want to train models with `past_covariates` (aka. external factors).

This time lets test with a **Recurrent Neural Network** which by default uses an `LSTM` backbone. We can also choose to test out a `GRU` backbone to experiment. Let's do both and see if we can improve our accuracy and reduce the overall MAPE. 

```
(🦋) /forecast/ $ rnn AAPL --forecast-only
Epoch 193: 100%|███████████████████████████████████████████████████████████| 25/25 [00:00<00:00, 129.49it/s, loss=-2.74, train_loss=-2.75, val_loss=-2.22]
Predicting RNN for 5 days                                                                                                                                 
100%|███████████████████████████████████████████████████████████████████████████████████████████████████████████████████| 115/115 [00:01<00:00, 86.89it/s]
RNN model obtains MAPE: 3.69% 


   Actual price: 157.37    
┏━━━━━━━━━━━━┳━━━━━━━━━━━━┓
┃ Datetime   ┃ Prediction ┃
┡━━━━━━━━━━━━╇━━━━━━━━━━━━┩
│ 2022-09-12 │ 155.71     │
├────────────┼────────────┤
│ 2022-09-13 │ 155.42     │
├────────────┼────────────┤
│ 2022-09-14 │ 155.11     │
├────────────┼────────────┤
│ 2022-09-15 │ 154.81     │
├────────────┼────────────┤
│ 2022-09-16 │ 154.51     │
└────────────┴────────────┘
```
<img width="791" alt="image" src="https://user-images.githubusercontent.com/105685594/189743690-2f1be795-437e-4e4f-992e-3e8ad4de62f6.png">

Seems like we improved the performance and reduced MAPE! 

Now for the second task, we would like to change the model type from `LSTM` --> `GRU`. Use the `-h` flag to understand the particular parameters one can change for RNN. (Please note that the parameters are different for each model).

```
(🦋) /forecast/ $ rnn -h
rnn -h
usage: rnn [--hidden-dim HIDDEN_DIM] [--training_length TRAINING_LENGTH] [--naive] [-d {AAPL,msft}] [-c TARGET_COLUMN] [-n N_DAYS] [-t TRAIN_SPLIT]
           [-i INPUT_CHUNK_LENGTH] [--force-reset FORCE_RESET] [--save-checkpoints SAVE_CHECKPOINTS] [--model-save-name MODEL_SAVE_NAME]
           [--n-epochs N_EPOCHS] [--model-type MODEL_TYPE] [--dropout DROPOUT] [--batch-size BATCH_SIZE] [--end S_END_DATE] [--start S_START_DATE]
           [--learning-rate LEARNING_RATE] [--residuals] [--forecast-only] [-h] [--export EXPORT]

Perform RNN forecast (Vanilla RNN, LSTM, GRU)

optional arguments:
  --hidden-dim HIDDEN_DIM
                        Size for feature maps for each hidden RNN layer (h_n) (default: 20)
  --training_length TRAINING_LENGTH
                        The length of both input (target and covariates) and output (target) time series used during training. Generally speaking,
                        training_length should have a higher value than input_chunk_length because otherwise during training the RNN is never run for as
                        many iterations as it will during training. (default: 20)
  --naive               Show the naive baseline for a model. (default: False)
  -d {AAPL,msft}, --target-dataset {AAPL,msft}
                        The name of the dataset you want to select (default: None)
  -c TARGET_COLUMN, --target-column TARGET_COLUMN
                        The name of the specific column you want to use (default: close)
  -n N_DAYS, --n-days N_DAYS
                        prediction days. (default: 5)
  -t TRAIN_SPLIT, --train-split TRAIN_SPLIT
                        Start point for rolling training and forecast window. 0.0-1.0 (default: 0.85)
  -i INPUT_CHUNK_LENGTH, --input-chunk-length INPUT_CHUNK_LENGTH
                        Number of past time steps for forecasting module at prediction time. (default: 14)
  --force-reset FORCE_RESET
                        If set to True, any previously-existing model with the same name will be reset (all checkpoints will be discarded). (default:
                        True)
  --save-checkpoints SAVE_CHECKPOINTS
                        Whether to automatically save the untrained model and checkpoints. (default: True)
  --model-save-name MODEL_SAVE_NAME
                        Name of the model to save. (default: rnn_model)
  --n-epochs N_EPOCHS   Number of epochs over which to train the model. (default: 300)
  --model-type MODEL_TYPE
                        Either a string specifying the RNN module type ("RNN", "LSTM" or "GRU") (default: LSTM)
  --dropout DROPOUT     Fraction of neurons afected by Dropout. (default: 0)
  --batch-size BATCH_SIZE
                        Number of time series (input and output) used in each training pass (default: 32)
  --end S_END_DATE      The end date (format YYYY-MM-DD) to select for testing (default: None)
  --start S_START_DATE  The start date (format YYYY-MM-DD) to select for testing (default: None)
  --learning-rate LEARNING_RATE
                        Learning rate during training. (default: 0.001)
  --residuals           Show the residuals for the model. (default: False)
  --forecast-only       Do not plot the hisotorical data without forecasts. (default: False)
  -h, --help            show this help message (default: False)
  --export EXPORT       Export figure into png, jpg, pdf, svg (default: )
```

Lets change the `--model-type` parameter to `GRU` and rerun. 

```
(🦋) /forecast/ $ rnn AAPL --model-type GRU --forecast-only
rnn AAPL --model-type GRU --forecast-only 
Epoch 35: 100%|████████████████████████████████████████████████████████████| 25/25 [00:00<00:00, 125.85it/s, loss=-2.72, train_loss=-2.74, val_loss=-2.13]
Predicting RNN for 5 days                                                                                                                                 
100%|███████████████████████████████████████████████████████████████████████████████████████████████████████████████████| 115/115 [00:01<00:00, 85.14it/s]
RNN model obtains MAPE: 3.64% 


   Actual price: 157.37    
┏━━━━━━━━━━━━┳━━━━━━━━━━━━┓
┃ Datetime   ┃ Prediction ┃
┡━━━━━━━━━━━━╇━━━━━━━━━━━━┩
│ 2022-09-12 │ 155.28     │
├────────────┼────────────┤
│ 2022-09-13 │ 155.02     │
├────────────┼────────────┤
│ 2022-09-14 │ 154.65     │
├────────────┼────────────┤
│ 2022-09-15 │ 154.30     │
├────────────┼────────────┤
│ 2022-09-16 │ 153.96     │
└────────────┴────────────┘
```
<img width="791" alt="image" src="https://user-images.githubusercontent.com/105685594/189745500-c079614c-9213-4fcb-8967-01a5b85a5722.png">

Looks like we squeezed out a little bit more accuracy! Good work. 

The take away for this is that all models should work out of the box when forecasting for a particular Timeseries. One can switch the target by specifying a `-c` for `TARGET_COLUMN` and test out performance with multiple different models with a single command. 

