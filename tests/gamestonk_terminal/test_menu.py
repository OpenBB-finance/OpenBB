import os
import warnings
import sys
import pytest

warnings.filterwarnings("ignore")
module_path = os.path.abspath(os.path.join("../.."))

if module_path not in sys.path:
    sys.path.append(module_path)
from terminal import menu


@pytest.mark.vcr(record_mode="none")
@pytest.mark.record_stdout
@pytest.mark.parametrize(
    "debug, test, filtert, path",
    (True, False, None, None),
    (False, False, None, "scripts/test_alt_covid.gst"),
    (False, True, "alt_covid", "scripts/"),
)
def test_menu(debug, test, filtert, path):
    menu(debug, test, filtert, path)
