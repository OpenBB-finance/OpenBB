"""Tests for the on-command-output plugin."""

import logging

from openbb_core.app.model.obbject import OBBject

from {{ cookiecutter.package_name }}.obbject.{{ cookiecutter.obbject_name }} import on_command_output


class TestNonblockingPlugin:
    """The plugin processes the output on a background thread."""

    def test_configuration(self):
        plugin = on_command_output.nonblocking_plugin
        assert plugin.on_command_output is True
        assert plugin.command_output_paths == ["/{{ cookiecutter.router_name }}/candles"]

    def test_processes_in_background(self, caplog):
        caplog.set_level(logging.INFO, logger=on_command_output.__name__)
        obbject = OBBject(results=[{"a": 1}, {"a": 2}], provider="demo")
        worker = obbject.nonblocking_plugin
        worker.join(timeout=5)
        assert not worker.is_alive()
        assert "Processed 2 rows from demo." in caplog.text
