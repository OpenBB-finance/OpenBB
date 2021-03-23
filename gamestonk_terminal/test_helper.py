""" Test helper """
__docformat__ = "numpy"

import pathlib
from typing import Callable
import yaml


def parametrize_from_file(test_namespace: str, parameter_file: str) -> Callable:
    """A test helper function returns a wrapper function that loads sets of parameters from a YAML and
    attaches test scenarios as metadata

    Parameters
    ----------
    test_namespace : str
        Test namespace to use within the YAML
    parameter_file : str
        Test scenario YAML to load

    Returns
    -------
    Callable
        Wrapper function
    """

    def wrapper(function):
        test_file_base_path = pathlib.Path(__file__).parent.absolute()
        data_file_full_path = pathlib.Path(test_file_base_path, parameter_file)

        with open(data_file_full_path, encoding="utf-8") as file:
            parameter_data = yaml.full_load(file)

        idlist = []
        argnames = []
        argvalues = []

        for scenario in parameter_data[test_namespace]:
            idlist.append(scenario)
            argnames = []
            tempvalues = []
            for argname in parameter_data[test_namespace][scenario].keys():
                argnames.append(argname)
                tempvalues.append(parameter_data[test_namespace][scenario][argname])
            argvalues.append(tempvalues)

        function.test_params_names = argnames
        function.test_param_values = argvalues
        function.test_ids = idlist

        return function

    return wrapper


def pytest_generate_tests(metafunc):
    """ https://docs.pytest.org/en/stable/parametrize.html#pytest-generate-tests """
    if getattr(metafunc.function, "test_params_names", None):
        metafunc.parametrize(
            metafunc.function.test_params_names,
            metafunc.function.test_param_values,
            ids=metafunc.function.test_ids,
            scope="class",
        )
