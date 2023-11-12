### THIS FILE IS AUTO-GENERATED. DO NOT EDIT. ###


from openbb_core.app.static.container import Container


class Extensions(Container):
    # fmt: off
    """
Routers:
    /crypto
    /currency
    /economy
    /equity
    /etf
    /fixedincome
    /index
    /news
    /regulators

Extensions:
    - crypto@0.1.0a4
    - currency@0.1.0a4
    - economy@0.1.0a4
    - equity@0.1.0a4
    - etf@0.1.0a4
    - fixedincome@0.1.0a4
    - index@0.1.0a4
    - news@0.1.0a4
    - regulators@0.1.0a4

    - benzinga@0.1.0a4
    - fmp@0.1.0a4
    - fred@0.1.0a4
    - intrinio@0.1.0a4
    - oecd@0.1.0a4
    - polygon@0.1.0a4
    - sec@0.1.0a4
    - tradingeconomics@0.1.0a4    """
    # fmt: on
    def __repr__(self) -> str:
        return self.__doc__ or ""

    @property
    def crypto(self):  # route = "/crypto"
        from . import crypto

        return crypto.ROUTER_crypto(command_runner=self._command_runner)

    @property
    def currency(self):  # route = "/currency"
        from . import currency

        return currency.ROUTER_currency(command_runner=self._command_runner)

    @property
    def economy(self):  # route = "/economy"
        from . import economy

        return economy.ROUTER_economy(command_runner=self._command_runner)

    @property
    def equity(self):  # route = "/equity"
        from . import equity

        return equity.ROUTER_equity(command_runner=self._command_runner)

    @property
    def etf(self):  # route = "/etf"
        from . import etf

        return etf.ROUTER_etf(command_runner=self._command_runner)

    @property
    def fixedincome(self):  # route = "/fixedincome"
        from . import fixedincome

        return fixedincome.ROUTER_fixedincome(command_runner=self._command_runner)

    @property
    def index(self):  # route = "/index"
        from . import index

        return index.ROUTER_index(command_runner=self._command_runner)

    @property
    def news(self):  # route = "/news"
        from . import news

        return news.ROUTER_news(command_runner=self._command_runner)

    @property
    def regulators(self):  # route = "/regulators"
        from . import regulators

        return regulators.ROUTER_regulators(command_runner=self._command_runner)
