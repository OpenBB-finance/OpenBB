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
(🦋) / $ <command> -h
```

### Loading Data

Importing data from within the terminal can be simply done as follows:

```
(🦋) / $ stocks
(🦋) / $ load AAPL
(🦋) / $ forecast
```
The menu can support loading in unlimited datasets. Once the first one is loaded, the menu options should turn blue to allow you to begin working through the menu options.

To load external data in the form as `.csv`, please place them into the folder shown within your terminal menu and then load them in as follows:

```
(🦋) / $ forecast
(🦋) / $ load msft.csv
```
<img width="1091" alt="image" src="https://user-images.githubusercontent.com/105685594/189728980-06ea171a-f088-4bd5-8849-2eadde984ad6.png">

### Understanding the structure of the menu 

The menu is broken up into three distinct sections. These sections represent the typical order of operations a machine learning professional would have to take in order to complete a project. 

Once data is loaded in, begin with `Exploration`.

`Exploration`: Explore the datasets loaded into the menu to further understand your data and create unique new datasets by combining and analyzing features. Functions to note: `plot`, `combine`, `desc`, `corr`
<img width="692" alt="image" src="https://user-images.githubusercontent.com/105685594/189729792-079f151e-f2b4-41bf-99d9-c83849c59170.png">


`Feature Engineering`: Manuipulate datasets (addition, deletion, combination, mutation) of your data set to potentially improve machine learning model training, by providing new features and covariates that may leading to better performance and greater accuracy.
<img width="694" alt="image" src="https://user-images.githubusercontent.com/105685594/189730399-fc4051f2-4d8e-4ff1-8494-44528d8f5513.png">


`TimeSeries Forecasting`: Train state of the art models on custom datasets and experiment tuning hyperparameters.
<img width="694" alt="image" src="https://user-images.githubusercontent.com/105685594/189730287-1c5c8141-1801-4a35-b9e9-acb32be35c13.png">





