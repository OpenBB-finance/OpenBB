import pytest


@pytest.fixture(scope="module")
def vcr_config():
    return {
        "filter_headers": [
            ("User-Agent", None),
            ("Authorization", "MOCK_AUTHORIZATION"),
        ],
    }


@pytest.fixture
def mock_compose_export_path(monkeypatch, tmp_path):
    # files in tmp_dir will remain (in separate folders) for 3 sequential runs of pytest
    def mock_return(func_name, *args, **kwargs):
        return tmp_path / f"20220829_235959_{func_name}"

    monkeypatch.setattr("openbb_terminal.helper_funcs.compose_export_path", mock_return)
