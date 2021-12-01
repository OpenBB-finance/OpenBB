# IMPORTATION STANDARD
import os
import pathlib
from typing import Any, Dict, List

# IMPORTATION THIRDPARTY
import pytest

# from pytest_recording._vcr import merge_kwargs
from _pytest.capture import MultiCapture, SysCapture
from _pytest.config import Config
from _pytest.fixtures import SubRequest
from _pytest.mark.structures import Mark

# IMPORTATION INTERNAL

# pylint: disable=redefined-outer-name


@pytest.fixture
def default_csv_path(request):
    module = request.node.fspath
    path = os.path.join(
        module.dirname,
        "csv",
        module.purebasename,
        request.node.name,
    )
    path += ".csv"

    # CREATE FOLDER
    if not os.path.exists(path):
        dir_name = os.path.dirname(path)
        pathlib.Path(dir_name).mkdir(parents=True, exist_ok=True)

    return path


@pytest.fixture
def default_txt_path(request):
    module = request.node.fspath
    path = os.path.join(
        module.dirname,
        "txt",
        module.purebasename,
        request.node.name,
    )
    path += ".txt"

    # CREATE FOLDER
    if not os.path.exists(path):
        dir_name = os.path.dirname(path)
        pathlib.Path(dir_name).mkdir(parents=True, exist_ok=True)

    return path


@pytest.fixture
def default_json_path(request):
    module = request.node.fspath
    path = os.path.join(
        module.dirname,
        "json",
        module.purebasename,
        request.node.name,
    )
    path += ".json"

    # CREATE FOLDER
    if not os.path.exists(path):
        dir_name = os.path.dirname(path)
        pathlib.Path(dir_name).mkdir(parents=True, exist_ok=True)

    return path


def pytest_configure(config: Config) -> None:
    config.addinivalue_line("markers", "record_stdout: Mark the test as text record.")


@pytest.fixture
def record_stdout_markers(request: SubRequest) -> List[Mark]:
    """All markers applied to the certain test together with cassette names associated with each marker."""
    return list(request.node.iter_markers(name="record_stdout"))


def merge_markers_kwargs(markers: List[Mark]) -> Dict[str, Any]:
    """Merge all kwargs into a single dictionary to pass to `vcr.use_cassette`."""
    kwargs: Dict[str, Any] = dict()
    for marker in reversed(markers):
        kwargs.update(marker.kwargs)
    return kwargs


def record_stdout_cmp_content(
    assert_in_list: List[str],
    captured_content: str,
    record_path: str,
    strip: bool,
):
    # COMPARE RECORD
    if os.path.exists(record_path):
        with open(file=record_path, encoding="utf-8") as f:
            record_content = f.read()
        if strip:
            assert captured_content.strip() == record_content.strip()
        else:
            assert captured_content == record_content

    # COMPARE ASSERT IN LIST
    for assert_in in assert_in_list:
        assert assert_in in captured_content


def record_stdout_save(
    captured_content: str,
    record_path: str,
    record_mode: str,
    save_record: bool,
):
    record_exists = os.path.exists(record_path)

    if record_exists:
        with open(file=record_path, encoding="utf-8") as f:
            record_content = f.read()
        unchanged = captured_content == record_content
    else:
        unchanged = False

    if not save_record:
        save = False
    elif record_mode == "all":
        save = True
    elif record_mode == "new_episodes":
        save = not record_exists or not unchanged
    elif record_mode == "none":
        save = False
        if not record_exists:
            raise Exception("You are using `record-mode=none`.")
    elif record_mode == "once":
        save = not record_exists
    elif record_mode == "rewrite":
        save = True
    else:
        raise Exception("Unknown `record-mode`.")

    if save:
        dir_name = os.path.dirname(record_path)
        pathlib.Path(dir_name).mkdir(parents=True, exist_ok=True)

        with open(file=record_path, mode="w", encoding="utf-8") as f:
            f.write(captured_content)


def record_stdout_format_kwargs(
    default_txt_path: str,
    record_mode: str,
    record_stdout_markers: List[Mark],
) -> Dict[str, Any]:
    kwargs = merge_markers_kwargs(record_stdout_markers)

    formatted_fields = dict()
    formatted_fields["assert_in_list"] = kwargs.get("assert_in_list", list())
    formatted_fields["record_mode"] = kwargs.get("record_mode", record_mode)
    formatted_fields["record_path"] = kwargs.get("record_path", default_txt_path)
    formatted_fields["save_record"] = kwargs.get("save_record", True)
    formatted_fields["strip"] = kwargs.get("strip", True)

    # MERGE `RECORD_NAME`
    if "record_name" in kwargs:
        if "record_path" in kwargs:
            raise Exception("You can't use both `record_name` and `record_path`.")

        dir_name = os.path.dirname(default_txt_path)
        formatted_fields["record_path"] = os.path.join(dir_name, kwargs["record_name"])

    # FORMAT `RECORD_PATH` EXTENSION
    if not formatted_fields["record_path"].endswith(".txt"):
        formatted_fields["record_path"] += ".txt"

    return formatted_fields


@pytest.fixture(autouse=True)
def record_stdout(
    default_txt_path: str,
    disable_recording: bool,
    record_stdout_markers: List[Mark],
    record_mode: str,
    request: SubRequest,
):
    marker = request.node.get_closest_marker("record_stdout")

    if disable_recording:
        yield None
    elif marker:
        # FORMAT MARKERS KEYWORD ARGUMENTS
        formatted_kwargs = record_stdout_format_kwargs(
            default_txt_path=default_txt_path,
            record_mode=record_mode,
            record_stdout_markers=record_stdout_markers,
        )

        # CAPTURE STDOUT
        capture = request.config.getoption("--capture")
        if capture == "no":
            global_capturing = MultiCapture(
                in_=SysCapture(0), out=SysCapture(1), err=SysCapture(2)
            )
            global_capturing.start_capturing()
            yield
            captured_content = global_capturing.readouterr().out
            global_capturing.stop_capturing()
        else:
            capsys = request.getfixturevalue("capsys")
            yield
            captured_content = capsys.readouterr().out

        # SAVE RECORD
        record_stdout_save(
            captured_content=captured_content,
            record_path=formatted_kwargs["record_path"],
            record_mode=formatted_kwargs["record_mode"],
            save_record=formatted_kwargs["save_record"],
        )

        # ASSERT CONTENT
        record_stdout_cmp_content(
            assert_in_list=formatted_kwargs["assert_in_list"],
            captured_content=captured_content,
            record_path=formatted_kwargs["record_path"],
            strip=formatted_kwargs["strip"],
        )
    else:
        yield None
