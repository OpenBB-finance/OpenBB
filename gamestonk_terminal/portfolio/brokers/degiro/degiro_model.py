# IMPORTATION STANDARD
import math

from typing import Union

# IMPORTATION THIRDPARTY
import pandas as pd
from degiro_connector.trading.helpers import payload_handler

from degiro_connector.trading.api import API as TradingAPI
from degiro_connector.trading.pb.trading_pb2 import (
    Credentials,
    LatestNews,
    NewsByCompany,
    Order,
    ProductsInfo,
    ProductSearch,
    TopNewsPreview,
    Update,
)

# IMPORTATION INTERNAL
import gamestonk_terminal.config_terminal as config

# pylint: disable=no-member
# pylint: disable=no-else-return


class DegiroModel:
    def __init__(self):
        self.__default_credentials = Credentials(
            int_account=None,
            username=config.DG_USERNAME,
            password=config.DG_PASSWORD,
            one_time_password=None,
            totp_secret_key=config.DG_TOTP_SECRET,
        )
        self.__trading_api = TradingAPI(
            credentials=self.__default_credentials,
        )

    def __hold_fetch_additional_information(
        self,
        positions: pd.DataFrame,
    ) -> pd.DataFrame:
        """Fetch extra information about the positions like :
            - name
            - isin
            - symbol
            - ...

        Parameters
        ----------
        positions : pd.DataFrame
            Positions from which we want extra fields.

        Returns
        -------
        pd.DataFrame
            Positions with additional data.
        """

        # GET ATTRIBUTES
        trading_api = self.__trading_api

        # EXTRACT POSITIONS IDS
        positions_ids = positions["id"].astype("int32").tolist()

        # FETCH EXTRA DATA
        request = ProductsInfo.Request()
        request.products.extend(positions_ids)
        products_info_pb = trading_api.get_products_info(
            request=request,
            raw=False,
        )

        # CONVERT TO DICT
        products_info_dict = payload_handler.message_to_dict(
            message=products_info_pb,
        )

        # CONVERT TO DATAFRAME
        products_info = pd.DataFrame(products_info_dict["values"].values())

        # MERGE DATA WITH POSITIONS
        positions_full = pd.merge(positions, products_info, on="id")

        return positions_full

    def __hold_fetch_current_positions(self) -> pd.DataFrame:
        # GET ATTRIBUTES
        trading_api = self.__trading_api

        # FETCH HELD PRODUCTS
        request_list = Update.RequestList()
        request_list.values.extend(
            [
                Update.Request(
                    option=Update.Option.PORTFOLIO,
                    last_updated=0,
                ),
            ]
        )

        update_pb = trading_api.get_update(
            request_list=request_list,
            raw=False,
        )

        # CHECK EMPTINESS
        if len(update_pb.portfolio.values) == 0:
            return pd.DataFrame()
        else:
            positions_partial = self.__hold_filter_current_positions(
                portfolio=update_pb.portfolio,
            )

            # FETCH ADDITIONAL DATA ON PRODUCTS
            positions = self.__hold_fetch_additional_information(
                positions=positions_partial,
            )

            return positions

    @staticmethod
    def __hold_filter_current_positions(
        portfolio: Update.Portfolio,
    ) -> pd.DataFrame:
        """Filter the positions in order to keep only held ones.

        Parameters
        ----------
        portfolio : Update.Portfolio
            Portfolio returned from the API.

        Returns
        -------
        pd.DataFrame
            Filtered portfolio.
        """

        # CONVERT TO DATAFRAME
        portfolio_dict = payload_handler.message_to_dict(message=portfolio)
        positions = pd.DataFrame(portfolio_dict["values"])

        # SETUP MASK
        mask_product = positions["positionType"] == "PRODUCT"
        mask_not_empty = positions["size"] > 0
        mask_current_position = mask_product & mask_not_empty

        # FILTER
        positions = positions[mask_current_position]

        return positions

    def __setup_extra_credentials(self):
        trading_api = self.__trading_api
        client_details_table = trading_api.get_client_details()
        int_account = client_details_table["data"]["intAccount"]
        trading_api.credentials.int_account = int_account

    def cancel(self, order_id: str) -> bool:
        return self.__trading_api.delete_order(order_id=order_id)

    def companynews(self, isin: str) -> NewsByCompany:
        trading_api = self.__trading_api
        request = NewsByCompany.Request(
            isin=isin,
            limit=10,
            offset=0,
            languages="en,fr",
        )

        # FETCH DATA
        news = trading_api.get_news_by_company(
            request=request,
            raw=False,
        )

        return news

    def create_calculate_product_id(
        self,
        product: int,
        symbol: str,
    ) -> Union[int, None]:
        trading_api = self.__trading_api

        if product is None:
            request_lookup = ProductSearch.RequestLookup(
                search_text=symbol,
                limit=1,
                offset=0,
                product_type_id=1,
            )

            products_lookup = trading_api.product_search(
                request=request_lookup,
                raw=False,
            )
            products_lookup_dict = payload_handler.message_to_dict(
                message=products_lookup,
            )
            product = products_lookup_dict["products"][0]

            if len(products_lookup.products) <= 0 or product["symbol"] != symbol:
                return None
            else:
                return int(product["id"])
        else:
            return product

    def create_calculate_size(
        self,
        price: float,
        size: int,
        up_to: float,
    ):
        if size is None:
            return math.floor(up_to / price)
        else:
            return size

    def create_check(self, order: Order) -> Union[Order.CheckingResponse, bool]:
        return self.__trading_api.check_order(order=order)

    def create_confirm(
        self,
        confirmation_id: str,
        order: Order,
    ) -> Union[Order.ConfirmationResponse, bool]:
        return self.__trading_api.confirm_order(
            confirmation_id=confirmation_id,
            order=order,
        )

    def hold_positions(self) -> pd.DataFrame:
        return self.__hold_fetch_current_positions()

    def lastnews(self, limit: int) -> LatestNews:
        trading_api = self.__trading_api
        request = LatestNews.Request(
            offset=0,
            languages="en,fr",
            limit=limit,
        )
        news = trading_api.get_latest_news(request=request, raw=False)

        return news

    def login(self, credentials: Credentials):
        self.__trading_api = TradingAPI(credentials=credentials)
        self.__trading_api.connect()
        self.__setup_extra_credentials()

    def login_default_credentials(self):
        return self.__default_credentials

    def logout(self) -> bool:
        return self.__trading_api.logout()

    def lookup(
        self,
        limit: int,
        offset: int,
        search_text: str,
    ) -> ProductSearch:
        trading_api = self.__trading_api
        request_lookup = ProductSearch.RequestLookup(
            search_text=search_text,
            limit=limit,
            offset=offset,
        )
        product_search = trading_api.product_search(
            request=request_lookup,
            raw=False,
        )

        return product_search

    def pending(self) -> Update.Orders:
        trading_api = self.__trading_api
        request_list = Update.RequestList()
        request_list.values.extend(
            [
                Update.Request(option=Update.Option.ORDERS, last_updated=0),
            ]
        )
        update = trading_api.get_update(request_list=request_list)

        return update.orders

    def topnews(self) -> TopNewsPreview:
        return self.__trading_api.get_top_news_preview(raw=False)

    def update(self, order: Order) -> Update.Orders:
        return self.__trading_api.update_order(order=order)

    def update_pending_order(self, order_id: str) -> Union[None, Order]:
        trading_api = self.__trading_api
        request_list = Update.RequestList()
        request_list.values.extend(
            [
                Update.Request(option=Update.Option.ORDERS, last_updated=0),
            ]
        )
        update = trading_api.get_update(request_list=request_list)

        if len(update.orders.values) > 0:
            for order in update.orders.values:
                if order.id == order_id:
                    return order
            return None
        else:
            return None
