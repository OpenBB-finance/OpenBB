from openbb_terminal.forecast import knn_view


def test_display_knn_forecast(tsla_csv):
    tsla_csv = tsla_csv.set_index("date")
    knn_view.display_k_nearest_neighbors(
        data=tsla_csv,
        target_column="close",
        ticker="TSLA",
        n_neighbors=3,
        n_input_days=3,
        n_predict_days=3,
        test_size=5,
    )
