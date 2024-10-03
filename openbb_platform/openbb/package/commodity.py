### THIS FILE IS AUTO-GENERATED. DO NOT EDIT. ###


from openbb_core.app.static.container import Container


class ROUTER_commodity(Container):
    """/commodity
    /price
    """

    def __repr__(self) -> str:
        return self.__doc__ or ""

    @property
    def price(self):
        # pylint: disable=import-outside-toplevel
        from . import commodity_price

        return commodity_price.ROUTER_commodity_price(
            command_runner=self._command_runner
        )
