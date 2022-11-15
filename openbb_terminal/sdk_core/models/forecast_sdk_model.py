# flake8: noqa
# pylint: disable=C0301,R0902,R0903
from openbb_terminal.sdk_core.sdk_helpers import Category
import openbb_terminal.sdk_core.sdk_init as lib


class ForecastRoot(Category):
    """OpenBB SDK Forecasting Module

    Attributes:
        `atr`: Calculate the Average True Range of a variable based on a a specific stock ticker.\n
        `brnn`: Performs Block RNN forecasting\n
        `brnn_view`: Display BRNN forecast\n
        `clean`: Clean up NaNs from the dataset\n
        `combine`: Adds the given column of df2 to df1\n
        `corr`: Returns correlation for a given df\n
        `corr_chart`: Plot correlation coefficients for dataset features\n
        `delta`: Calculate the %change of a variable based on a specific column\n
        `desc`: Returns statistics for a given df\n
        `ema`: A moving average provides an indication of the trend of the price movement\n
        `expo`: Performs Probabilistic Exponential Smoothing forecasting\n
        `expo_view`: Display Probabilistic Exponential Smoothing forecast\n
        `linregr`: Perform Linear Regression Forecasting\n
        `linregr_view`: Display Linear Regression Forecasting\n
        `load`: Load custom file into dataframe.\n
        `mom`: A momentum oscillator, which measures the percentage change between the current\n
        `nbeats`: Perform NBEATS Forecasting\n
        `nbeats_view`: Display NBEATS forecast\n
        `nhits`: Performs Nhits forecasting\n
        `nhits_view`: Display Nhits forecast\n
        `plot`: Plot data from a dataset\n
        `regr`: Perform Regression Forecasting\n
        `regr_view`: Display Regression Forecasting\n
        `rename`: Rename a column in a dataframe\n
        `rnn`: Perform RNN forecasting\n
        `rnn_view`: Display RNN forecast\n
        `roc`: A momentum oscillator, which measures the percentage change between the current\n
        `rsi`: A momentum indicator that measures the magnitude of recent price changes to evaluate\n
        `season`: Plot seasonality from a dataset\n
        `signal`: A price signal based on short/long term price.\n
        `sto`: Stochastic Oscillator %K and %D : A stochastic oscillator is a momentum indicator comparing a particular closing\n
        `tcn`: Perform TCN forecasting\n
        `tcn_view`: Display TCN forecast\n
        `tft`: Performs Temporal Fusion Transformer forecasting\n
        `tft_view`: Display Temporal Fusion Transformer forecast\n
        `theta`: Performs Theta forecasting\n
        `theta_view`: Display Theta forecast\n
        `trans`: Performs Transformer forecasting\n
        `trans_view`: Display Transformer forecast\n
    """

    def __init__(self):
        super().__init__()
        if lib.FORECASTING:
            self.atr = lib.forecast_model.add_atr
            self.brnn = lib.forecast_brnn_model.get_brnn_data
            self.brnn_view = lib.forecast_brnn_view.display_brnn_forecast
            self.clean = lib.forecast_model.clean
            self.combine = lib.forecast_model.combine_dfs
            self.corr = lib.forecast_model.corr_df
            self.corr_chart = lib.forecast_view.display_corr
            self.delete = lib.forecast_model.delete_column
            self.delta = lib.forecast_model.add_delta
            self.desc = lib.forecast_model.describe_df
            self.ema = lib.forecast_model.add_ema
            self.expo = lib.forecast_expo_model.get_expo_data
            self.expo_view = lib.forecast_expo_view.display_expo_forecast
            self.export = lib.forecast_view.export_df
            self.linregr = lib.forecast_linregr_model.get_linear_regression_data
            self.linregr_view = lib.forecast_linregr_view.display_linear_regression
            self.load = lib.common_model.load
            self.mom = lib.forecast_model.add_momentum
            self.nbeats = lib.forecast_nbeats_model.get_NBEATS_data
            self.nbeats_view = lib.forecast_nbeats_view.display_nbeats_forecast
            self.nhits = lib.forecast_nhits_model.get_nhits_data
            self.nhits_view = lib.forecast_nhits_view.display_nhits_forecast
            self.plot = lib.forecast_view.display_plot
            self.regr = lib.forecast_regr_model.get_regression_data
            self.regr_view = lib.forecast_regr_view.display_regression
            self.rename = lib.forecast_model.rename_column
            self.rnn = lib.forecast_rnn_model.get_rnn_data
            self.rnn_view = lib.forecast_rnn_view.display_rnn_forecast
            self.roc = lib.forecast_model.add_roc
            self.rsi = lib.forecast_model.add_rsi
            self.season = lib.forecast_view.display_seasonality
            self.show = lib.forecast_view.show_df
            self.signal = lib.forecast_model.add_signal
            self.sto = lib.forecast_model.add_sto
            self.tcn = lib.forecast_tcn_model.get_tcn_data
            self.tcn_view = lib.forecast_tcn_view.display_tcn_forecast
            self.tft = lib.forecast_tft_model.get_tft_data
            self.tft_view = lib.forecast_tft_view.display_tft_forecast
            self.theta = lib.forecast_theta_model.get_theta_data
            self.theta_view = lib.forecast_theta_view.display_theta_forecast
            self.trans = lib.forecast_trans_model.get_trans_data
            self.trans_view = lib.forecast_trans_view.display_trans_forecast
