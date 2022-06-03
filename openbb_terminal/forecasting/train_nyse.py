import pandas as pd
from darts import TimeSeries
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from pytorch_lightning.callbacks.early_stopping import EarlyStopping
from darts.dataprocessing.transformers import Scaler, MissingValuesFiller
from darts.models import NBEATSModel # NN 
from darts.metrics import mape, r2_score
from darts import concatenate
import glob


ticker_csvs = glob.glob("/home/martin/ai/stocks_training/nyse/*")

filler = MissingValuesFiller()

ticker_name_arr = []

ticker_scalers_arr = [] # for each timeseries, we keep our scaler 

 # for each covariate array, we keep our scaler 
covariate_scaler_vol_arr = []
covariate_scaler_open_arr = []
covariate_scaler_high_arr = [] 
covariate_scaler_low_arr = [] 
covariate_scaler_close_arr = [] 

time_series_whole = []
time_series_train = []
time_series_test = []

covariates_whole = [] # [[ts1], [ts2], [ts#]]
covariates_train = []
covariates_test = []

train_split = 0.95

for ticker in ticker_csvs:
    
    # read csv and convert to df
    df = pd.read_csv(ticker, delimiter=",")
    if df.empty:
        ticker_name = ticker.split('/')[-1].split('.')[0]
        print(f"Ticker {ticker_name} is empty.")
        continue

    ticker_scaler = Scaler()
    ticker_name = ticker.split('/')[-1].split('.')[0]
    ticker_name_arr.append(ticker_name)

    # Create a scaled timeSeries, specifying the time and value columns + scaling and filling in nans
    scaled_time_series_whole = ticker_scaler.fit_transform(
        filler.transform(
            TimeSeries.from_dataframe(
                df,
                time_col="Date",
                value_cols=["Adj Close"],
                freq="B",
                fill_missing_dates=True,)
            )
        ).astype(np.float32)

    scaled_time_series_train, scaled_time_series_test = scaled_time_series_whole.split_before(train_split)
    ticker_scalers_arr.append(ticker_scaler)
    time_series_whole.append(scaled_time_series_whole)
    time_series_train.append(scaled_time_series_train)
    time_series_test.append(scaled_time_series_test)


    # create scaled covariates #########
    # building Volume covariate ------------------------------
    covariate_vol_scaler = Scaler()
    scaled_covariate_vol_whole = covariate_vol_scaler.fit_transform(
        filler.transform(
            TimeSeries.from_dataframe(
                df,
                time_col="Date",
                value_cols=["Volume"],
                freq="B",
                fill_missing_dates=True,
            )
        )
    ).astype(np.float32)

    scaled_covariate_vol_train, scaled_covariate_vol_test = scaled_covariate_vol_whole.split_before(train_split)
    covariate_scaler_vol_arr.append(covariate_vol_scaler)


    # building open covariate ------------------------------
    covariate_open_scaler = Scaler()
    scaled_covariate_open_whole = covariate_open_scaler.fit_transform(
        filler.transform(
            TimeSeries.from_dataframe(
                df,
                time_col="Date",
                value_cols=["Open"],
                freq="B",
                fill_missing_dates=True,
            )
        )
    ).astype(np.float32)

    scaled_covariate_open_train, scaled_covariate_open_test = scaled_covariate_open_whole.split_before(train_split)
    covariate_scaler_open_arr.append(covariate_open_scaler)
    
    # building high covariate ------------------------------
    covariate_high_scaler = Scaler()
    scaled_covariate_high_whole = covariate_high_scaler.fit_transform(
        filler.transform(
            TimeSeries.from_dataframe(
                df,
                time_col="Date",
                value_cols=["High"],
                freq="B",
                fill_missing_dates=True,
            )
        )
    ).astype(np.float32)

    scaled_covariate_high_train, scaled_covariate_high_test = scaled_covariate_high_whole.split_before(train_split)
    covariate_scaler_high_arr.append(covariate_high_scaler)

    # building low covariate ------------------------------
    covariate_low_scaler = Scaler()
    scaled_covariate_low_whole = covariate_low_scaler.fit_transform(
        filler.transform(
            TimeSeries.from_dataframe(
                df,
                time_col="Date",
                value_cols=["Low"],
                freq="B",
                fill_missing_dates=True,
            )
        )
    ).astype(np.float32)

    scaled_covariate_low_train, scaled_covariate_low_test = scaled_covariate_low_whole.split_before(train_split)
    covariate_scaler_low_arr.append(covariate_low_scaler)

    # building close covariate ------------------------------
    covariate_close_scaler = Scaler()
    scaled_covariate_close_whole = covariate_close_scaler.fit_transform(
        filler.transform(
            TimeSeries.from_dataframe(
                df,
                time_col="Date",
                value_cols=["Close"],
                freq="B",
                fill_missing_dates=True,
            )
        )
    ).astype(np.float32)

    scaled_covariate_close_train, scaled_covariate_close_test = scaled_covariate_close_whole.split_before(train_split)
    covariate_scaler_close_arr.append(covariate_close_scaler)
    


    ### DONE BUILDING COVS
    # concat all covariates together
    scaled_covariate_concat_whole = concatenate([scaled_covariate_vol_whole, 
                                                 scaled_covariate_open_whole, 
                                                 scaled_covariate_high_whole,
                                                 scaled_covariate_low_whole,
                                                 scaled_covariate_close_whole
                                                 ], axis=1) 
    
    scaled_covariate_concat_train = concatenate([scaled_covariate_vol_train, 
                                                 scaled_covariate_open_train, 
                                                 scaled_covariate_high_train,
                                                 scaled_covariate_low_train,
                                                 scaled_covariate_close_train
                                                 ], axis=1) 
    
    scaled_covariate_concat_test = concatenate([scaled_covariate_vol_test, 
                                                scaled_covariate_open_test, 
                                                scaled_covariate_high_test,
                                                scaled_covariate_low_test,
                                                scaled_covariate_close_test
                                                ], axis=1) 
    
    # pass in concatenated series into one multi-series covariate for this specific Timeseries
    covariates_whole.append(scaled_covariate_concat_whole)
    covariates_train.append(scaled_covariate_concat_train)
    covariates_test.append(scaled_covariate_concat_test)

    print(f"finished with ticker: {ticker_name}")    
    

# plot whole ts
# for i,ts in enumerate(time_series_whole):
#     ts.plot(label=f"{ticker_name_arr[i]}")

print(f"Total ts in whole: {len(time_series_whole)}")
print(f"Total ts in training: {len(time_series_train)}")
print(f"Total ts in testing:  {len(time_series_test)}")
print(f"Total covarients in whole: {len(covariates_whole)}")
print(f"Total covarients in train: {len(covariates_train)}")
print(f"Total covarients in test: {len(covariates_test)}")

# Early Stopping
my_stopper = EarlyStopping(
                    monitor="val_loss",
                    patience=5,
                    min_delta=0.05,
                    mode='min',
                )
pl_trainer_kwargs={"callbacks": [my_stopper],
                    "accelerator": "gpu",
                    "gpus": [0]}

multiseries_nbeats = NBEATSModel(
    input_chunk_length=30,
    output_chunk_length=7,
    generic_architecture=True,
    num_stacks=10,
    num_blocks=3,
    num_layers=4,
    layer_widths=512,
    n_epochs=100,
    nr_epochs_val_period=1,
    batch_size=800,
    model_name="nbeats_run",
    force_reset=True,
    save_checkpoints=True,
    random_state = 42,
    pl_trainer_kwargs=pl_trainer_kwargs
)

multiseries_nbeats.fit(series = time_series_train,
                       val_series = time_series_test,
                       past_covariates=covariates_train,
                       val_past_covariates=covariates_test)

# Load best model 
multiseries_nbeats = NBEATSModel.load_from_checkpoint(multiseries_nbeats.model_name, best=False)

# save best model
multiseries_nbeats.save_model(path="multi_series.pth.tar")

# load the saved model 
best_multiseries_nbeats = NBEATSModel.load_model("multi_series.pth.tar")

# grab first test time series 
actual_ts_whole = time_series_whole[0]
actual_ts_train = time_series_train[0]
actual_ts_test = time_series_test[0]
actual_covariates_whole = covariates_whole[0] # get all of the covariates since we need to have them to predict the last 10%

# forecast the first timeseries
forecast_ts = best_multiseries_nbeats.predict(len(actual_ts_test) + 7, 
                                              series = actual_ts_train,
                                              past_covariates=actual_covariates_whole) 

backtest_cov = best_multiseries_nbeats.backtest(
    actual_ts_whole,
    past_covariates=actual_covariates_whole,
    start=train_split,
    forecast_horizon=7,
    stride=7,
    retrain=False,
    verbose=True,
)

#actual_ts_whole.plot(label="actual")
print(f"Back test = {backtest_cov}")

actual_ts_test.plot(label='actual')
forecast_ts.plot(label = "forecast")
print(f"MAPE = {mape(actual_series = actual_ts_test, pred_series = forecast_ts ):.2f}%")
plt.legend()
