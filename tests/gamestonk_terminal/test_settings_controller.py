from unittest.mock import patch
from gamestonk_terminal import settings_controller


@patch("dotenv.set_key")
@patch("os.path.exists")
def test_call_directory(path_mock, set_key_mock):
    path_mock.return_value = True
    sc = settings_controller.SettingsController()
    sc.call_directory(["--path", "test-path"])
    assert set_key_mock.called_once_with(
        sc.env_file, "GTFF_AUTOSAVE_DIRECTORY", "test-path"
    )


@patch("dotenv.set_key")
@patch("gamestonk_terminal.feature_flags.ENABLE_AUTOSAVE", False)
def test_call_autosave(set_key_mock):
    sc = settings_controller.SettingsController()
    sc.call_autosave(None)
    assert set_key_mock.called_once_with(sc.env_file, "GTFF_ENABLE_AUTOSAVE", True)
    sc.call_autosave(None)
    assert set_key_mock.called_once_with(sc.env_file, "GTFF_ENABLE_AUTOSAVE", False)
