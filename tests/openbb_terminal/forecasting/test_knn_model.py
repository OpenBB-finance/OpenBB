from openbb_terminal.forecasting import knn_model


def test_get_knn_model(recorder, tsla_csv):
    df = tsla_csv.set_index("date")
    value = knn_model.get_knn_model_data(
        df["close"],
        n_input_days=5,
        n_predict_days=5,
        n_neighbors=5,
        test_size=0.5,
        end_date=None,
        no_shuffle=True,
    )

    recorder.capture(value[0].values.tolist())
