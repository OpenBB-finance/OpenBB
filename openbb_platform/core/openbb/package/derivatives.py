### THIS FILE IS AUTO-GENERATED. DO NOT EDIT. ###


from openbb_core.app.static.container import Container


class ROUTER_derivatives(Container):
    """/derivatives
    /futures
    /options
    """

    def __repr__(self) -> str:
        return self.__doc__ or ""

    @property
    def futures(self):
        # pylint: disable=import-outside-toplevel
        from . import derivatives_futures

        return derivatives_futures.ROUTER_derivatives_futures(
            command_runner=self._command_runner
        )

    @property
    def options(self):
        # pylint: disable=import-outside-toplevel
        from . import derivatives_options

        return derivatives_options.ROUTER_derivatives_options(
            command_runner=self._command_runner
        )
