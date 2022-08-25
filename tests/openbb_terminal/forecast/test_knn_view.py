import pytest

try:
    from openbb_terminal.forecast import knn_view
except ImportError:
    pytest.skip(allow_module_level=True)


def test_display_knn_forecast(tsla_csv):
    tsla_csv = tsla_csv.set_index("date")
    knn_view.display_k_nearest_neighbors(
        data=tsla_csv,
        target_column="close",
        n_neighbors=3,
        input_chunk_length=5,
        n_predict=3,
        test_size=5,
    )
