### THIS FILE IS AUTO-GENERATED. DO NOT EDIT. ###



from openbb_core.app.static.container import Container


class Extensions(Container):
    """
    /crypto
    /economy
    /fixedincome
    /forex
    /futures
    /news
    /qa
    /stocks
    /ta
    """

    def __repr__(self) -> str:
        return self.__doc__ or ""

    @property
    def crypto(self):  # route = "/crypto"
        from openbb_core.app.static.package import crypto

        return crypto.CLASS_crypto(command_runner=self._command_runner)

    @property
    def economy(self):  # route = "/economy"
        from openbb_core.app.static.package import economy

        return economy.CLASS_economy(command_runner=self._command_runner)

    @property
    def fixedincome(self):  # route = "/fixedincome"
        from openbb_core.app.static.package import fixedincome

        return fixedincome.CLASS_fixedincome(command_runner=self._command_runner)

    @property
    def forex(self):  # route = "/forex"
        from openbb_core.app.static.package import forex

        return forex.CLASS_forex(command_runner=self._command_runner)

    @property
    def futures(self):  # route = "/futures"
        from openbb_core.app.static.package import futures

        return futures.CLASS_futures(command_runner=self._command_runner)

    @property
    def news(self):  # route = "/news"
        from openbb_core.app.static.package import news

        return news.CLASS_news(command_runner=self._command_runner)

    @property
    def qa(self):  # route = "/qa"
        from openbb_core.app.static.package import qa

        return qa.CLASS_qa(command_runner=self._command_runner)

    @property
    def stocks(self):  # route = "/stocks"
        from openbb_core.app.static.package import stocks

        return stocks.CLASS_stocks(command_runner=self._command_runner)

    @property
    def ta(self):  # route = "/ta"
        from openbb_core.app.static.package import ta

        return ta.CLASS_ta(command_runner=self._command_runner)
