To obtain charts, make sure to add `chart=True` as the last parameter

## Get underlying data 
### forecast.rnn(data: Union[pandas.core.series.Series, pandas.core.frame.DataFrame], target_column: str = 'close', n_predict: int = 5, train_split: float = 0.85, forecast_horizon: int = 5, model_type: str = 'LSTM', hidden_dim: int = 20, dropout: float = 0.0, batch_size: int = 16, n_epochs: int = 100, learning_rate: float = 0.001, model_save_name: str = 'rnn_model', training_length: int = 20, input_chunk_size: int = 14, force_reset: bool = True, save_checkpoints: bool = True) -> Tuple[List[darts.timeseries.TimeSeries], List[darts.timeseries.TimeSeries], List[darts.timeseries.TimeSeries], Optional[float], Any]

Perform RNN forecasting

    Args:
        data (Union[pd.Series, pd.DataFrame]):
            Input Data
        n_predict (int, optional):
            Days to predict. Defaults to 5.
        target_column (str, optional):
            Target column to forecast. Defaults to "close".
        train_split (float, optional):
            Train/val split. Defaults to 0.85.
        forecast_horizon (int, optional):
            Forecast horizon when performing historical forecasting. Defaults to 5.
        model_type (str, optional):
            Either a string specifying the RNN module type ("RNN", "LSTM" or "GRU"). Defaults to "LSTM".
        hidden_dim (int, optional):
            Size for feature maps for each hidden RNN layer.. Defaults to 20.
        dropout (float, optional):
            Fraction of neurons afected by Dropout. Defaults to 0.0.
        batch_size (int, optional):
            Number of time series (input and output sequences) used in each training pass. Defaults to 32.
        n_epochs (int, optional):
            Number of epochs over which to train the model. Defaults to 100.
        learning_rate (float, optional):
            Defaults to 1e-3.
        model_save_name (str, optional):
            Name for model. Defaults to "brnn_model".
        force_reset (bool, optional):
            If set to True, any previously-existing model with the same name will be reset
            (all checkpoints will be discarded). Defaults to True.
        save_checkpoints (bool, optional):
            Whether or not to automatically save the untrained model and checkpoints from training.
            Defaults to True.

    Returns:
        List[TimeSeries]
            Adjusted Data series
        List[TimeSeries]
            Historical forecast by best RNN model
        List[TimeSeries]
            list of Predictions
        float
            Mean average precision error
        Any
            Best RNN Model

## Getting charts 
### forecast.rnn(data: Union[pandas.core.frame.DataFrame, pandas.core.series.Series], target_column: str = 'close', dataset_name: str = '', n_predict: int = 5, train_split: float = 0.85, forecast_horizon: int = 5, model_type: str = 'LSTM', hidden_dim: int = 20, dropout: float = 0.0, batch_size: int = 16, n_epochs: int = 100, learning_rate: float = 0.001, model_save_name: str = 'rnn_model', training_length: int = 20, input_chunk_size: int = 14, force_reset: bool = True, save_checkpoints: bool = True, export: str = '', residuals: bool = False, forecast_only: bool = False, start_date: Optional[datetime.datetime] = None, end_date: Optional[datetime.datetime] = None, naive: bool = False, export_pred_raw: bool = False, external_axes: Optional[List[axes]] = None, chart=True)

Display RNN forecast

    Parameters
    ----------
        data (Union[pd.Series, pd.DataFrame]):
            Input Data
        dataset_name str
            The name of the ticker to be predicted
        n_predict (int, optional):
            Days to predict. Defaults to 5.
        target_column (str, optional):
            Target column to forecast. Defaults to "close".
        train_split (float, optional):
            Train/val split. Defaults to 0.85.
        forecast_horizon (int, optional):
            Forecast horizon when performing historical forecasting. Defaults to 5.
        model_type (str, optional):
            Either a string specifying the RNN module type ("RNN", "LSTM" or "GRU"). Defaults to "LSTM".
        hidden_dim (int, optional):
            Size for feature maps for each hidden RNN layer.. Defaults to 20.
        dropout (float, optional):
            Fraction of neurons afected by Dropout. Defaults to 0.0.
        batch_size (int, optional):
            Number of time series (input and output sequences) used in each training pass. Defaults to 32.
        n_epochs (int, optional):
            Number of epochs over which to train the model. Defaults to 100.
        learning_rate (float, optional):
            Defaults to 1e-3.
        model_save_name (str, optional):
            Name for model. Defaults to "brnn_model".
        force_reset (bool, optional):
            If set to True, any previously-existing model with the same name will be reset
            (all checkpoints will be discarded). Defaults to True.
        save_checkpoints (bool, optional):
            Whether or not to automatically save the untrained model and checkpoints from training. Defaults to True.
        forecast_only: bool
            Whether to only show dates in the forecasting range. Defaults to False.
        export: str
            Format to export data
        residuals: bool
            Whether to show residuals for the model. Defaults to False.
        start_date: Optional[datetime]
            The starting date to perform analysis, data before this is trimmed. Defaults to None.
        end_date: Optional[datetime]
            The ending date to perform analysis, data after this is trimmed. Defaults to None.
        naive: bool
            Whether to show the naive baseline. This just assumes the closing price will be the same
            as the previous day's closing price. Defaults to False.
        external_axes:Optional[List[plt.axes]]
            External axes to plot on
