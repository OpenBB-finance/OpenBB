"""Argument removal must update argparse's actual parsing behavior."""

from argparse import ArgumentParser

import pytest

from openbb_cli.argparse_translator.utils import remove_argument


@pytest.mark.parametrize("identifier", ["mode", "--mode", "-m"])
def test_remove_argument_disables_all_aliases(identifier):
    parser = ArgumentParser()
    group = parser.add_mutually_exclusive_group()
    action = group.add_argument("-m", "--mode", choices=["fast", "slow"])
    remove_argument(parser, identifier)
    for option in ["-m", "--mode"]:
        with pytest.raises(SystemExit):
            parser.parse_args([option, "fast"])
    assert action not in group._group_actions
    assert "--mode" not in parser.format_help()
    assert vars(parser.parse_args([])) == {}


def test_unknown_argument_preserves_parser():
    parser = ArgumentParser()
    parser.add_argument("--mode")
    assert remove_argument(parser, "unknown") == []
    assert parser.parse_args(["--mode", "fast"]).mode == "fast"
