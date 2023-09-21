### THIS FILE IS AUTO-GENERATED. DO NOT EDIT. ###


from openbb_core.app.static.container import Container


class Extensions(Container):
    # fmt: off
    """
    /crypto
    /economy
    /fixedincome
    /forex
    /news
    /stocks

Extensions:
    - crypto@0.1.0a0
    - economy@0.1.0a0
    - fixedincome@0.1.0a0
    - forex@0.1.0a0
    - news@0.1.0a0
    - stocks@0.1.0a1

    - benzinga@0.1.0a1
    - fmp@0.1.0a1
    - fred@0.1.0a0
    - intrinio@0.1.0a1
    - polygon@0.1.0a1    """
    # fmt: on
    def __repr__(self) -> str:
        return self.__doc__ or ""

    @property
    def crypto(self):  # route = "/crypto"
        from . import crypto

        return crypto.CLASS_crypto(command_runner=self._command_runner)

    @property
    def economy(self):  # route = "/economy"
        from . import economy

        return economy.CLASS_economy(command_runner=self._command_runner)

    @property
    def fixedincome(self):  # route = "/fixedincome"
        from . import fixedincome

        return fixedincome.CLASS_fixedincome(command_runner=self._command_runner)

    @property
    def forex(self):  # route = "/forex"
        from . import forex

        return forex.CLASS_forex(command_runner=self._command_runner)

    @property
    def news(self):  # route = "/news"
        from . import news

        return news.CLASS_news(command_runner=self._command_runner)

    @property
    def stocks(self):  # route = "/stocks"
        from . import stocks

        return stocks.CLASS_stocks(command_runner=self._command_runner)
