### THIS FILE IS AUTO-GENERATED. DO NOT EDIT. ###


from openbb_core.app.static.container import Container


class ROUTER_derivatives(Container):
    """/derivatives
    /options
    """

    def __repr__(self) -> str:
        return self.__doc__ or ""

    @property
    def options(self):  # route = "/derivatives/options"
        from . import derivatives_options

        return derivatives_options.ROUTER_derivatives_options(
            command_runner=self._command_runner
        )
