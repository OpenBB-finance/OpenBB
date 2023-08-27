# IMPORTATION STANDARD
import datetime
import logging
import math
from pathlib import Path
from typing import List, Union

# IMPORTATION THIRDPARTY
import pandas as pd
from degiro_connector.core.helpers import pb_handler
from degiro_connector.trading.api import API as TradingAPI
from degiro_connector.trading.models.trading_pb2 import (
    Credentials,
    LatestNews,
    NewsByCompany,
    Order,
    ProductSearch,
    ProductsInfo,
    TopNewsPreview,
    TransactionsHistory,
    Update,
)

from openbb_terminal.core.session.current_user import get_current_user

# IMPORTATION INTERNAL
from openbb_terminal.decorators import log_start_end
from openbb_terminal.portfolio import portfolio_helper
from openbb_terminal.rich_config import console

# pylint: disable=no-member,no-else-return


logger = logging.getLogger(__name__)


class DegiroModel:
    @log_start_end(log=logger)
    def __init__(self):
        self.__default_credentials = self.get_default_credentials()
        self.__trading_api = self.get_default_trading_api()

    def get_default_credentials(self):
        """
        Generate default credentials object from config file

        Returns:
            Credentials: credentials object with default settings
        """
        current_user = get_current_user()
        topt_key = current_user.credentials.DG_TOTP_SECRET
        totp_secret_key = None if topt_key == "REPLACE_ME" else topt_key

        return Credentials(
            int_account=None,
            username=current_user.credentials.DG_USERNAME,
            password=current_user.credentials.DG_PASSWORD,
            one_time_password=None,
            totp_secret_key=totp_secret_key,
        )

    def get_default_trading_api(self):
        """
        Generate default trading api object from config file

        Returns:
            TradingAPI: trading api object with default settings
        """
        return TradingAPI(
            credentials=self.__default_credentials,
        )

    @log_start_end(log=logger)
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
        ----------
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
        products_info_dict = pb_handler.message_to_dict(
            message=products_info_pb,
        )

        # CONVERT TO DATAFRAME
        products_info = pd.DataFrame(products_info_dict["values"].values())

        # MERGE DATA WITH POSITIONS
        positions_full = pd.merge(positions, products_info, on="id")

        return positions_full

    @log_start_end(log=logger)
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
    @log_start_end(log=logger)
    def __hold_filter_current_positions(
        portfolio: Update.Portfolio,
    ) -> pd.DataFrame:
        """Filter the positions in order to keep only held ones.

        Parameters
        ----------
        portfolio : Update.Portfolio
            Portfolio returned from the API.

        Returns
        ----------
        pd.DataFrame
            Filtered portfolio.
        """

        # CONVERT TO DATAFRAME
        portfolio_dict = pb_handler.message_to_dict(message=portfolio)
        positions = pd.DataFrame(portfolio_dict["values"])

        # SETUP MASK
        mask_product = positions["positionType"] == "PRODUCT"
        mask_not_empty = positions["size"] > 0
        mask_current_position = mask_product & mask_not_empty

        # FILTER
        positions = positions[mask_current_position]

        return positions

    @log_start_end(log=logger)
    def __setup_extra_credentials(self):
        trading_api = self.__trading_api
        client_details_table = trading_api.get_client_details()
        int_account = client_details_table["data"]["intAccount"]
        trading_api.credentials.int_account = int_account

    @log_start_end(log=logger)
    def cancel(self, order_id: str) -> bool:
        return self.__trading_api.delete_order(order_id=order_id)

    @log_start_end(log=logger)
    def companynews(
        self, symbol: str, limit: int = 10, offset: int = 0, languages: str = "en,fr"
    ) -> NewsByCompany:
        trading_api = self.__trading_api
        request = NewsByCompany.Request(
            isin=symbol,
            limit=limit,
            offset=offset,
            languages=languages,
        )

        # FETCH DATA
        try:
            news = trading_api.get_news_by_company(
                request=request,
                raw=False,
            )
        except Exception as e:
            e_str = str(e)
            console.print(f"[red]{e_str}[/red]")
            news = None

        return news

    @log_start_end(log=logger)
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
            products_lookup_dict = pb_handler.message_to_dict(
                message=products_lookup,
            )
            product = products_lookup_dict["products"][0]

            if len(products_lookup.products) <= 0 or product["symbol"] != symbol:
                return None
            else:
                return int(product["id"])
        else:
            return product

    @log_start_end(log=logger)
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

    @log_start_end(log=logger)
    def create_check(self, order: Order) -> Union[Order.CheckingResponse, bool]:
        return self.__trading_api.check_order(order=order)

    @log_start_end(log=logger)
    def create_confirm(
        self,
        confirmation_id: str,
        order: Order,
    ) -> Union[Order.ConfirmationResponse, bool]:
        return self.__trading_api.confirm_order(
            confirmation_id=confirmation_id,
            order=order,
        )

    @log_start_end(log=logger)
    def hold_positions(self) -> pd.DataFrame:
        if self.check_session_id():
            return self.__hold_fetch_current_positions()
        return pd.DataFrame()

    @log_start_end(log=logger)
    def lastnews(self, limit: int) -> LatestNews:
        trading_api = self.__trading_api
        request = LatestNews.Request(
            offset=0,
            languages="en,fr",
            limit=limit,
        )
        news = trading_api.get_latest_news(request=request, raw=False)

        return news

    @log_start_end(log=logger)
    def login(self):
        self.__trading_api.connect()
        self.__setup_extra_credentials()

    @log_start_end(log=logger)
    def login_default_credentials(self):
        return self.__default_credentials

    @log_start_end(log=logger)
    def logout(self) -> bool:
        return self.__trading_api.logout()

    @log_start_end(log=logger)
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

    @log_start_end(log=logger)
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

    @log_start_end(log=logger)
    def topnews(self) -> TopNewsPreview:
        return self.__trading_api.get_top_news_preview(raw=False)

    @log_start_end(log=logger)
    def update(self, order: Order) -> Update.Orders:
        return self.__trading_api.update_order(order=order)

    @log_start_end(log=logger)
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

    @log_start_end(log=logger)
    def get_transactions(
        self, start: datetime.date, end: datetime.date
    ) -> pd.DataFrame:
        trading_api = self.__trading_api

        from_date = TransactionsHistory.Request.Date(
            year=start.year,
            month=start.month,
            day=start.day,
        )
        to_date = TransactionsHistory.Request.Date(
            year=end.year,
            month=end.month,
            day=end.day,
        )
        request = TransactionsHistory.Request(
            from_date=from_date,
            to_date=to_date,
        )

        transactions_dict = trading_api.get_transactions_history(
            request=request,
            raw=True,
        )

        transactions_df = pd.DataFrame(transactions_dict["data"])
        transactions_df["productId"] = transactions_df["productId"].astype("int")

        return transactions_df

    @log_start_end(log=logger)
    def get_products_details(self, product_id_list: List[int]) -> pd.DataFrame:
        trading_api = self.__trading_api

        product_id_list = list(set(product_id_list))

        request = ProductsInfo.Request()
        request.products.extend(product_id_list)

        products_info = trading_api.get_products_info(
            request=request,
            raw=True,
        )

        products_df = pd.DataFrame(products_info["data"].values())

        return products_df

    @log_start_end(log=logger)
    def get_transactions_export(
        self, start: datetime.date, end: datetime.date, currency: str
    ) -> pd.DataFrame:
        transactions_df = self.get_transactions(start=start, end=end)
        product_id_list = list(transactions_df.productId)
        products_df = self.get_products_details(product_id_list=product_id_list)

        products_df["productId"] = products_df["id"]
        transactions_df["productId"] = transactions_df["productId"].astype("int")
        products_df["productId"] = products_df["productId"].astype("int")
        transactions_full_df = pd.merge(
            transactions_df,
            products_df[{"productId", "symbol", "productType", "isin"}],
            on="productId",
        )

        portfolio_df = transactions_full_df.rename(
            columns={
                "date": "Date",
                "isin": "ISIN",
                "symbol": "Ticker",
                "productType": "Type",  # STOCK or ETF
                "price": "Price",
                "quantity": "Quantity",
                "buysell": "Side",  # BUY or SELL
                "totalFeesInBaseCurrency": "Fees",
            }
        )

        portfolio_df["Premium"] = 0
        portfolio_df["Currency"] = currency
        portfolio_df["Side"] = portfolio_df["Side"].replace({"S": "SELL", "B": "BUY"})
        portfolio_df["Date"] = pd.to_datetime(
            portfolio_df["Date"].str.slice(0, 10)
        ).dt.date
        columns = [
            "Date",
            "ISIN",
            "Ticker",
            "Type",
            "Price",
            "Quantity",
            "Fees",
            "Premium",
            "Side",
            "Currency",
        ]
        portfolio_df = portfolio_df[columns]
        portfolio_df = portfolio_df.set_index("Date")

        return portfolio_df

    @staticmethod
    @log_start_end(log=logger)
    def export_data(portfolio_df: pd.DataFrame, export: str = ""):
        # In this scenario the path was provided, e.g. --export pt.csv, pt.jpg

        if "." in export:
            if export.endswith("csv"):
                filename = export
            # In this scenario we use the default filename
            else:
                console.print("Wrong export file specified.\n")
        else:
            now = datetime.datetime.now()
            filename = f"{now.strftime('%Y%m%d_%H%M%S')}_paexport_degiro.csv"

        file_path = Path(str(portfolio_helper.DEFAULT_HOLDINGS_PATH), filename)

        portfolio_df.to_csv(file_path)

        console.print(f"Saved file: {file_path}\n")

    @log_start_end(log=logger)
    def check_session_id(self) -> bool:
        trading_api = self.__trading_api

        if trading_api.connection_storage.session_id:
            return True
        return False

    @log_start_end(log=logger)
    def reset_sessionid_and_creds(self):
        # Setting the session_id to None
        trading_api = self.__trading_api
        trading_api.connection_storage.session_id = None

        # Resetting the object after logout
        self.__default_credentials = self.get_default_credentials()
        self.__trading_api = self.get_default_trading_api()

    @log_start_end(log=logger)
    def check_credentials(self):
        self.login()
        if self.check_session_id():
            self.logout()
            return True
        else:
            return False
