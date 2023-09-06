"""Test the utils.py file."""
# pylint: disable=redefined-outer-name


from pathlib import Path
from unittest.mock import PropertyMock, mock_open, patch

import pytest
from importlib_metadata import EntryPoint, EntryPoints
from openbb_core.app.static.build_utils import auto_build, get_ext_map, package_diff
from openbb_core.env import Env

PATH = "openbb_core.app.static.build_utils."


@pytest.fixture(scope="function")
def tmp_dir(tmp_path_factory):
    return tmp_path_factory.mktemp("tmp_dir")


def test_get_ext_map(tmp_dir):
    """Test extensions map."""

    open_mock = mock_open()
    with patch(PATH + "open", open_mock), patch(PATH + "load") as mock_load:
        get_ext_map(package=tmp_dir)
        open_mock.assert_called_once_with(Path(tmp_dir, "extension_map.json"))
        mock_load.assert_called_once()


@pytest.mark.parametrize(
    "ext_built, ext_installed, ext_inst_version, expected_add, expected_remove",
    [
        (
            {
                "openbb_core_extension": [
                    "ext_1@0.0.0",
                    "ext_2@0.0.0",
                ],
                "openbb_provider_extension": [
                    "prov_1@0.0.0",
                    "prov_2@1.1.1",
                ],
            },
            EntryPoints(
                (
                    EntryPoint(
                        name="ext_2", value="...", group="openbb_core_extension"
                    ),
                    EntryPoint(
                        name="prov_2", value="...", group="openbb_provider_extension"
                    ),
                )
            ),
            "0.0.0",
            {"prov_2@0.0.0"},
            {"ext_1@0.0.0", "prov_1@0.0.0", "prov_2@1.1.1"},
        ),
        (
            {
                "openbb_core_extension": ["ext_1@9.9.9"],
                "openbb_provider_extension": ["prov_2@0.0.0"],
            },
            EntryPoints(
                (
                    EntryPoint(
                        name="ext_2", value="...", group="openbb_core_extension"
                    ),
                    EntryPoint(
                        name="prov_1", value="...", group="openbb_provider_extension"
                    ),
                )
            ),
            "5.5.5",
            {"ext_2@5.5.5", "prov_1@5.5.5"},
            {"ext_1@9.9.9", "prov_2@0.0.0"},
        ),
    ],
)
def test_package_diff(
    tmp_dir,
    ext_built,
    ext_installed,
    ext_inst_version,
    expected_add,
    expected_remove,
):
    """Test package differences."""

    def mock_entry_points(group):
        return ext_installed.select(**{"group": group})

    with patch(PATH + "get_ext_map") as mock_get_ext_map, patch(
        PATH + "entry_points", mock_entry_points
    ), patch.object(EntryPoint, "dist", new_callable=PropertyMock) as mock_obj:

        class MockPathDistribution:
            version = ext_inst_version

        mock_obj.return_value = MockPathDistribution()
        mock_get_ext_map.return_value = ext_built

        add, remove = package_diff(tmp_dir)

        # We add whatever is not built, but is installed
        assert add == expected_add
        # We remove whatever is built, but is not installed
        assert remove == expected_remove


@pytest.mark.parametrize(
    "add, remove, openbb_auto_build",
    [
        (set(), set(), True),
        ({"this"}, set(), True),
        (set(), {"that"}, True),
        ({"this"}, {"that"}, True),
        ({"this"}, {"that"}, False),
    ],
)
def test_auto_build(tmp_dir, add, remove, openbb_auto_build):
    """Test auto build."""

    with patch(PATH + "package_diff") as mock_package_diff, patch(
        PATH + "build"
    ) as mock_build, patch.object(Env, "AUTO_BUILD", openbb_auto_build):
        mock_package_diff.return_value = add, remove
        auto_build(tmp_dir)

    if openbb_auto_build:
        mock_package_diff.assert_called_once_with(Path(tmp_dir, "package"))
        if add or remove:
            mock_build.assert_called_once_with(tmp_dir)
    else:
        mock_package_diff.assert_not_called()
        mock_build.assert_not_called()
