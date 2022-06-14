import numpy as np
from darts.dataprocessing.transformers import Scaler
from darts import TimeSeries
from pytorch_lightning.callbacks.early_stopping import EarlyStopping
from openbb_terminal.rich_config import console


def scaled_past_covs(past_covariates, filler, data, train_split):
    if past_covariates is not None:
        covariates_scalers = []  # to hold all temp scalers in case we need them
        target_covariates_names = past_covariates.split(",")

        # create first covariate to then stack onto
        past_covariate_scaler = Scaler()
        console.print(f"[green]Covariate #0: {target_covariates_names[0]}[/green]")
        scaled_past_covariate_whole = past_covariate_scaler.fit_transform(
            filler.transform(
                TimeSeries.from_dataframe(
                    data,
                    time_col="date",
                    value_cols=target_covariates_names[0],
                    freq="B",
                    fill_missing_dates=True,
                )
            )
        ).astype(np.float32)

        if len(target_covariates_names) > 1:
            for i, column in enumerate(target_covariates_names[1:]):
                console.print(f"[green]Covariate #{i+1}: {column}[/green]")
                _temp_scaler = Scaler()
                covariates_scalers.append(_temp_scaler)
                _temp_new_scaled_covariate = _temp_scaler.fit_transform(
                    filler.transform(
                        TimeSeries.from_dataframe(
                            data,
                            time_col="date",
                            value_cols=[column],
                            freq="B",
                            fill_missing_dates=True,
                        )
                    )
                ).astype(np.float32)

                # continually stack covariates based on column names
                scaled_past_covariate_whole = scaled_past_covariate_whole.stack(
                    _temp_new_scaled_covariate
                )

        # Split the full scale covariate to train and val
        (
            scaled_past_covariate_train,
            scaled_past_covariate_val,
        ) = scaled_past_covariate_whole.split_before(train_split)
        return (
            scaled_past_covariate_whole,
            scaled_past_covariate_train,
            scaled_past_covariate_val,
        )


def early_stopper(patience: int):
    my_stopper = EarlyStopping(
        monitor="val_loss",
        patience=patience,
        min_delta=0,
        mode="min",
    )
    return my_stopper
