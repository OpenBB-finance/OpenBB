### THIS FILE IS AUTO-GENERATED. DO NOT EDIT. ###


from openbb_core.app.static.container import Container


class ROUTER_regulators(Container):
    """/regulators
    /cftc
    /sec
    """

    def __repr__(self) -> str:
        return self.__doc__ or ""

    @property
    def cftc(self):
        # pylint: disable=import-outside-toplevel
        from . import regulators_cftc

        return regulators_cftc.ROUTER_regulators_cftc(
            command_runner=self._command_runner
        )

    @property
    def sec(self):
        # pylint: disable=import-outside-toplevel
        from . import regulators_sec

        return regulators_sec.ROUTER_regulators_sec(command_runner=self._command_runner)
