# IMPORTS STANDARD

import json
import os
import pathlib
from typing import Any, Dict, List, Optional, Type

import importlib_metadata

# IMPORTS THIRD-PARTY
import matplotlib
import pandas as pd
import pytest
import yfinance.utils
from _pytest.capture import MultiCapture, SysCapture
from _pytest.config import Config
from _pytest.config.argparsing import Parser
from _pytest.fixtures import SubRequest
from _pytest.mark.structures import Mark

# IMPORTS INTERNAL
from openbb_terminal import (
    config_terminal,
    decorators,
    helper_funcs,
)
from openbb_terminal.core.session.current_system import set_system_variable

# pylint: disable=redefined-outer-name

config_terminal.setup_i18n()

DISPLAY_LIMIT: int = 500
EXTENSIONS_ALLOWED: List[str] = ["csv", "json", "txt"]
EXTENSIONS_MATCHING: Dict[str, List[Type]] = {
    "csv": [pd.DataFrame, pd.Series],
    "json": [bool, dict, float, int, list, tuple],
    "txt": [str],
}

set_system_variable("TEST_MODE", True)
set_system_variable("LOG_COLLECT", False)


class Record:
    @staticmethod
    def extract_string(data: Any, **kwargs) -> str:
        if isinstance(data, tuple(EXTENSIONS_MATCHING["txt"])):
            string_value = data
        elif isinstance(data, tuple(EXTENSIONS_MATCHING["csv"])):
            string_value = data.to_csv(
                encoding="utf-8",
                lineterminator="\n",
                # date_format="%Y-%m-%d %H:%M:%S",
                **kwargs,
            )
        elif isinstance(data, tuple(EXTENSIONS_MATCHING["json"])):
            string_value = json.dumps(data, **kwargs)
        else:
            raise AttributeError(f"Unsupported type : {type(data)}")

        return string_value.replace("\r\n", "\n")

    @staticmethod
    def load_string(path: str) -> Optional[str]:
        if os.path.exists(path):
            with open(
                file=path,
                encoding="utf-8",
                newline="\n",  # Windows: newline="\r\n" Which is BAD
            ) as f:
                return f.read()
        else:
            return None

    @property
    def captured(self) -> str:
        return self.__captured

    @property
    def strip(self) -> bool:
        return self.__strip

    @property
    def record_changed(self) -> bool:
        return (
            self.__recorded is None
            or (self.__strip and self.__recorded.strip() != self.__captured.strip())
            or (not self.__strip and self.__recorded != self.__captured)
        )

    @property
    def record_exists(self) -> bool:
        return self.__recorded is not None

    @property
    def record_path(self) -> str:
        return self.__record_path

    @property
    def recorded(self) -> Optional[str]:
        return self.__recorded

    def recorded_reload(self):
        record_path = self.__record_path
        self.__recorded = self.load_string(path=record_path)

    def __init__(
        self, captured: Any, record_path: str, strip: bool = False, **kwargs
    ) -> None:
        self.__captured = self.extract_string(data=captured, **kwargs)
        self.__record_path = record_path
        self.__strip = strip

        self.__recorded = self.load_string(path=record_path)

    def persist(self):
        record_path = self.__record_path
        captured = self.__captured
        record_dir_name = os.path.dirname(record_path)

        # CREATE FOLDER
        if not os.path.exists(record_dir_name):
            pathlib.Path(record_dir_name).mkdir(parents=True, exist_ok=True)

        # SAVE FILE
        with open(
            file=record_path,
            mode="w",
            encoding="utf-8",
            newline="\n",  # Windows: newline="\r\n" Which is BAD
        ) as f:
            f.write(captured)

        # RELOAD RECORDED CONTENT
        self.recorded_reload()


class PathTemplate:
    @staticmethod
    def find_extension(data: Any):
        for extension, type_list in EXTENSIONS_MATCHING.items():
            if isinstance(data, tuple(type_list)):
                return extension
        raise Exception(f"No extension found for this type : {type(data)}")

    def __init__(self, module_dir: str, module_name: str, test_name: str) -> None:
        self.__module_dir = module_dir
        self.__module_name = module_name
        self.__test_name = test_name

    def build_path_by_extension(self, extension: str, index: int = 0):
        if extension not in EXTENSIONS_ALLOWED:
            raise Exception(f"Unsupported extension : {extension}")

        path = os.path.join(
            self.__module_dir, extension, self.__module_name, self.__test_name
        )
        if index:
            path += "_" + str(index)
        path += "."
        path += extension

        return path

    def build_path_by_data(self, data: Any, index: int = 0):
        extension = self.find_extension(data=data)
        return self.build_path_by_extension(extension=extension, index=index)


class Recorder:
    @property
    def display_limit(self) -> int:
        return self.__display_limit

    @display_limit.setter
    def display_limit(self, display_limit: int):
        self.__display_limit = display_limit

    @property
    def rewrite_expected(self) -> bool:
        return self.__rewrite_expected

    @rewrite_expected.setter
    def rewrite_expected(self, rewrite_expected: bool):
        self.__rewrite_expected = rewrite_expected

    @property
    def path_template(self) -> PathTemplate:
        return self.__path_template

    @property
    def record_mode(self) -> str:
        return self.__record_mode

    @record_mode.setter
    def record_mode(self, record_mode: str):
        self.__record_mode = record_mode

    def __init__(
        self,
        path_template: PathTemplate,
        record_mode: str,
        display_limit: int = DISPLAY_LIMIT,
        rewrite_expected: bool = False,
    ) -> None:
        self.__path_template = path_template
        self.__record_mode = record_mode
        self.__display_limit = display_limit
        self.__rewrite_expected = rewrite_expected

        self.__record_list: List[Record] = list()

    def capture(self, captured: Any, strip: bool = False, **kwargs):
        record_list = self.__record_list
        record_path = self.__path_template.build_path_by_data(
            data=captured, index=len(record_list)
        )
        record = Record(
            captured=captured, record_path=record_path, strip=strip, **kwargs
        )
        self.__record_list.append(record)

    def capture_list(self, captured_list: List[Any], strip: bool = False):
        for captured in captured_list:
            self.capture(captured=captured, strip=strip)

    def assert_equal(self):
        record_list = self.__record_list

        for record in record_list:
            if record.record_changed:
                raise AssertionError(
                    "Change detected\n"
                    f"Record    : {record.record_path}\n"
                    f"Expected  : {record.recorded[:self.display_limit]}\n"
                    f"Actual    : {record.captured[:self.display_limit]}\n"
                )

    def assert_in_list(self, in_list: List[str]):
        record_list = self.__record_list

        for record in record_list:
            for string_value in in_list:
                assert string_value in record.captured

    def persist(self):
        record_list = self.__record_list
        record_mode = self.__record_mode
        rewrite_expected = self.__rewrite_expected

        for record in record_list:
            if record_mode == "all":
                save = True
            elif record_mode == "new_episodes":
                save = record.record_changed
            elif record_mode == "none":
                if not record.record_exists:
                    raise Exception("You are using `record-mode=none`.")

                save = False
            elif record_mode == "once":
                save = not record.record_exists
            elif record_mode == "rewrite":
                save = True
            else:
                raise Exception(f"Unknown `record-mode` : {record_mode}")

            if save or rewrite_expected:
                record.persist()


def build_path_by_extension(
    request: SubRequest, extension: str, create_folder: bool = False
) -> str:
    # SETUP PATH TEMPLATE
    module_dir = request.node.fspath.dirname
    module_name = request.node.fspath.purebasename
    test_name = request.node.name
    path_template = PathTemplate(
        module_dir=module_dir, module_name=module_name, test_name=test_name
    )

    # BUILD PATH
    path = path_template.build_path_by_extension(extension)

    # CREATE FOLDER
    if create_folder:
        dir_name = os.path.dirname(path)
        if not os.path.exists(dir_name):
            dir_name = os.path.dirname(path)
            pathlib.Path(dir_name).mkdir(parents=True, exist_ok=True)

    return path


def merge_markers_kwargs(markers: List[Mark]) -> Dict[str, Any]:
    """Merge all kwargs into a single dictionary."""
    kwargs: Dict[str, Any] = dict()
    for marker in reversed(markers):
        kwargs.update(marker.kwargs)
    return kwargs


def record_stdout_format_kwargs(
    test_name: str, record_mode: str, record_stdout_markers: List[Mark]
) -> Dict[str, Any]:
    kwargs = merge_markers_kwargs(record_stdout_markers)

    formatted_fields = dict()
    formatted_fields["assert_in_list"] = kwargs.get("assert_in_list", list())
    formatted_fields["display_limit"] = kwargs.get("display_limit", DISPLAY_LIMIT)
    formatted_fields["record_mode"] = kwargs.get("record_mode", record_mode)
    formatted_fields["record_name"] = kwargs.get("record_name", test_name)
    formatted_fields["save_record"] = kwargs.get("save_record", True)
    formatted_fields["strip"] = kwargs.get("strip", True)

    return formatted_fields


def pytest_addoption(parser: Parser):
    parser.addoption(
        "--forecast",
        action="store_true",
        help="To run tests with the marker : @pytest.mark.forecast",
    )
    parser.addoption(
        "--optimization",
        action="store_true",
        help="To run tests with the marker : @pytest.mark.optimization",
    )
    parser.addoption(
        "--session",
        action="store_true",
        help="To run tests with the marker : @pytest.mark.session",
    )
    parser.addoption(
        "--rewrite-expected",
        action="store_true",
        help="To force `record_stdout` and `recorder` to rewrite all files.",
    )
    parser.addoption(
        "--autodoc",
        action="store_true",
        default=False,
        help="run auto documentation tests",
    )


def brotli_check():
    for item in importlib_metadata.packages_distributions():
        if "brotli" in str(item).lower():
            pytest.exit("Uninstall brotli and brotlipy before running tests")


def disable_rich():
    def effect(df, *xargs, **kwargs):  # pylint: disable=unused-argument
        print(df.to_string())  # noqa: T201

    helper_funcs.print_rich_table = effect


def disable_matplotlib():
    # We add this to avoid multiple figures being opened
    matplotlib.use("Agg")


def disable_check_api():
    decorators.disable_check_api()


def enable_debug():
    set_system_variable("DEBUG_MODE", True)


def pytest_configure(config: Config) -> None:
    config.addinivalue_line("markers", "record_stdout: Mark the test as text record.")

    brotli_check()
    enable_debug()
    disable_rich()
    disable_check_api()
    disable_matplotlib()


@pytest.fixture(scope="session")  # type: ignore
def rewrite_expected(request: SubRequest) -> bool:
    """Force rewriting of all expected data by : `record_stdout` and `recorder`."""
    return request.config.getoption("--rewrite-expected")


@pytest.fixture(autouse=True)
def mock_matplotlib(mocker):
    mocker.patch("matplotlib.pyplot.show")


@pytest.fixture(autouse=True)
def mock_plotly(mocker):
    mocker.patch("plotly.io.show")


# pylint: disable=protected-access
@pytest.fixture(autouse=True)
def mock_yfinance_tzcache(mocker):
    mocker.patch.object(
        target=yfinance.utils,
        attribute="_TzCache",
        new=yfinance.utils._TzCacheDummy,
    )


@pytest.fixture
def default_csv_path(request: SubRequest) -> str:
    return build_path_by_extension(request=request, extension="csv", create_folder=True)


@pytest.fixture
def default_txt_path(request: SubRequest) -> str:
    return build_path_by_extension(request=request, extension="txt", create_folder=True)


@pytest.fixture
def default_json_path(request: SubRequest) -> str:
    return build_path_by_extension(
        request=request, extension="json", create_folder=True
    )


@pytest.fixture
def record_stdout_markers(request: SubRequest) -> List[Mark]:
    """All markers applied to the certain test together with cassette names associated with each marker."""
    return list(request.node.iter_markers(name="record_stdout"))


@pytest.fixture(autouse=True)
def record_stdout(
    disable_recording: bool,
    rewrite_expected: bool,
    record_stdout_markers: List[Mark],
    record_mode: str,
    request: SubRequest,
):
    marker = request.node.get_closest_marker("record_stdout")

    if disable_recording:
        yield None
    elif marker:
        # SETUP TEST DETAILS
        module_dir = request.node.fspath.dirname
        module_name = request.node.fspath.purebasename
        test_name = request.node.name

        # FORMAT MARKER'S KEYWORD ARGUMENTS
        formatted_kwargs = record_stdout_format_kwargs(
            test_name=test_name,
            record_mode=record_mode,
            record_stdout_markers=record_stdout_markers,
        )

        # SETUP RECORDER
        path_template = PathTemplate(
            module_dir=module_dir,
            module_name=module_name,
            test_name=formatted_kwargs["record_name"],
        )
        recorder = Recorder(
            path_template=path_template,
            record_mode=formatted_kwargs["record_mode"],
            display_limit=formatted_kwargs["display_limit"],
            rewrite_expected=rewrite_expected,
        )

        # CAPTURE STDOUT
        capture = request.config.getoption("--capture")
        if capture == "no":
            global_capturing = MultiCapture(
                in_=SysCapture(0), out=SysCapture(1), err=SysCapture(2)
            )
            global_capturing.start_capturing()
            yield
            recorder.capture(
                captured=global_capturing.readouterr().out,
                strip=formatted_kwargs["strip"],
            )
            global_capturing.stop_capturing()
        else:
            capsys = request.getfixturevalue("capsys")
            yield
            recorder.capture(
                captured=capsys.readouterr().out, strip=formatted_kwargs["strip"]
            )

        # SAVE/CHECK RECORD
        if formatted_kwargs["save_record"]:
            recorder.persist()
            recorder.assert_equal()
            recorder.assert_in_list(in_list=formatted_kwargs["assert_in_list"])
        else:
            recorder.assert_in_list(in_list=formatted_kwargs["assert_in_list"])
    else:
        yield None


@pytest.fixture
def recorder(
    disable_recording: bool,
    rewrite_expected: bool,
    record_mode: str,
    request: SubRequest,
):
    marker_record_stdout = request.node.get_closest_marker("record_stdout")
    module_dir = request.node.fspath.dirname
    module_name = request.node.fspath.purebasename
    test_name = request.node.name
    path_template = PathTemplate(
        module_dir=module_dir, module_name=module_name, test_name=test_name
    )
    if disable_recording:
        yield None
    elif marker_record_stdout:
        raise Exception(
            "You can't combine both of these fixtures : `record_stdout marker`, `recorder`."
        )
    else:
        recorder = Recorder(
            path_template, record_mode, rewrite_expected=rewrite_expected
        )
        yield recorder
        recorder.persist()
        recorder.assert_equal()
