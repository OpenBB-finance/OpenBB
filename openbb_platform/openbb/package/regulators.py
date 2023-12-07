### THIS FILE IS AUTO-GENERATED. DO NOT EDIT. ###


from openbb_core.app.static.container import Container


class ROUTER_regulators(Container):
    """/regulators
    /sec
    """

    def __repr__(self) -> str:
        return self.__doc__ or ""

    @property
    def sec(self):
        # pylint: disable=import-outside-toplevel
        from . import regulators_sec

        return regulators_sec.ROUTER_regulators_sec(command_runner=self._command_runner)
