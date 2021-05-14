import gamestonk_terminal.config_terminal as config
import pandas as pd
import quotecast.helpers.pb_handler as pb_handler

from quotecast.api import API as QuotecastAPI
from trading.api import API as TradingAPI
from trading.pb.trading_pb2 import (
    Credentials,
    LatestNews,
    NewsByCompany,
    ProductsInfo,
    ProductSearch,
    Update,
)

# SETUP CREDENTIALS
credentials = Credentials(
    int_account=None,
    username=config.DG_USERNAME,
    password=config.DG_PASSWORD,
    one_time_password=config.DG_TOTP,
    totp_secret_key=config.DG_TOTP_SECRET,
)

# SETUP TRADING API
trading_api = TradingAPI(credentials=credentials)

# DEFINE QUOTECAST API
quotecast_api = None


def fetch_additional_information(
    positions: pd.DataFrame,
) -> pd.DataFrame:
    """ Fetch extra information about the positions like :
        - name
        - isin
        - symbol
        - ...

    Args:
        positions (pd.DataFrame):
            Positions from which we want extra fields.

    Returns:
        pd.DataFrame: Positions with additional data.
    """

    # EXTRACT POSITIONS IDS
    positions_ids = positions['id'].astype('int32').tolist()

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
    products_info = pd.DataFrame(products_info_dict['values'].values())

    # MERGE DATA WITH POSITIONS
    positions_full = pd.merge(positions, products_info, on='id')

    return positions_full


def fetch_current_positions() -> pd.DataFrame:
    # FETCH HELD PRODUCTS
    request_list = Update.RequestList()
    request_list.values.extend([
        Update.Request(option=Update.Option.PORTFOLIO, last_updated=0),
    ])

    update_pb = trading_api.get_update(request_list=request_list, raw=False)
    positions_partial = filter_current_positions(portfolio=update_pb.portfolio)

    # FETCH ADDITIONAL DATA ON PRODUCTS
    positions = fetch_additional_information(positions=positions_partial)

    return positions


def filter_current_positions(
    portfolio: Update.Portfolio,
) -> pd.DataFrame:
    """ Filter the positions in order to keep only held ones.

    Args:
        portfolio (Update.Portfolio):
            Portfolio returned from the API.

    Returns:
        pd.DataFrame: Filtered portfolio.
    """

    # CONVERT TO DATAFRAME
    portfolio_dict = pb_handler.message_to_dict(message=portfolio)
    positions = pd.DataFrame(portfolio_dict['values'])

    # SETUP MASK
    mask_product = positions['positionType'] == 'PRODUCT'
    mask_not_empty = positions['size'] > 0
    mask_current_position = mask_product & mask_not_empty

    # FILTER
    positions = positions[mask_current_position]

    return positions


def login():
    """
        Connect to Degiro's API.
    """

    # CONNECT
    trading_api.connect()

    # FETCH CLIENT DETAILS
    client_details_table = trading_api.get_client_details()

    # EXTRACT OPTIONAL CREDENTIALS
    int_account = client_details_table['data']['intAccount']
    user_token = client_details_table['data']['id']

    # SETUP OPTIONAL CREDENTIALS
    trading_api.credentials.int_account = int_account
    quotecast_api = QuotecastAPI(user_token=user_token)  # noqa: F841


def logout():
    """
        Log out from Degiro's API.
    """

    trading_api.logout()


def show_holdings():
    """
        Display held products.
    """

    # FETCH HELD PRODUCTS
    positions = fetch_current_positions()

    # FORMAT DATAFRAME
    selected_columns = [
        'symbol',
        'size',
        'price',
        'closePrice',
        'breakEvenPrice',
    ]
    formatted_columns = [
        'Stonk',
        'Size',
        'Last Price',
        'Close Price',
        'Break Even Price',
    ]
    fmt_positions = positions[selected_columns].copy(deep=True)
    fmt_positions.columns = formatted_columns

    fmt_positions['% Change'] = positions['price']
    fmt_positions['% Change'] -= fmt_positions['Close Price']
    fmt_positions['% Change'] /= fmt_positions['Close Price']
    fmt_positions['% Change'] = fmt_positions['% Change'].round(3)

    # DISPLAY DATAFRAME
    print(fmt_positions)


def return_holdings() -> pd.DataFrame:
    # FETCH HELD PRODUCTS
    positions = fetch_current_positions()

    # FORMAT DATAFRAME
    selected_columns = [
        'symbol',
        'size',
        'price',
        'breakEvenPrice',
    ]
    formatted_columns = [
        'Symbol',
        'MarketValue',
        'Quantity',
        'CostBasis',
    ]
    fmt_positions = positions[selected_columns].copy(deep=True)
    fmt_positions.columns = formatted_columns
    fmt_positions['Broker'] = 'dg'

    return fmt_positions


def top_news_preview():
    """
        Display pending orders.
    """

    # FETCH DATA
    top_news_preview = trading_api.get_top_news_preview(raw=True)

    # DISPLAY DATA
    for article in top_news_preview['data']['items']:
        print('date', article['date'])
        print('lastUpdated', article['lastUpdated'])
        print('category', article['category'])
        print('title', article['title'])
        print('brief', article['brief'])
        print('---')


def product_lookup(search_text: str):
    # SETUP REQUEST
    request_lookup = ProductSearch.RequestLookup(
        search_text=search_text,
        limit=10,
        offset=0,
    )

    # FETCH DATA
    products = trading_api.product_search(
        request=request_lookup,
        raw=True,
    )

    # DISPLAY DATA
    products_df = pd.DataFrame(products['products'])
    products_selected = products_df[[
        'name',
        'isin',
        'symbol',
        'productType',
        'currency',
        'closePrice',
        'closePriceDate',
    ]]

    print(products_selected)


def latest_news():
    # SETUP REQUEST
    request = LatestNews.Request(
        offset=0,
        languages='en,fr',
        limit=20,
    )

    # FETCH DATA
    latest_news = trading_api.get_latest_news(request=request, raw=True)

    # DISPLAY DATA
    for article in latest_news['data']['items']:
        print('date', article['date'])
        print('title', article['title'])
        print('content', article['content'])
        print('---')


def news_by_company(isin: str):
    request = NewsByCompany.Request(
        isin=isin,
        limit=10,
        offset=0,
        languages='en,fr',
    )

    # FETCH DATA
    news_by_company = trading_api.get_news_by_company(
        request=request,
        raw=True,
    )

    # DISPLAY DATA
    for article in news_by_company['data']['items']:
        print('date', article['date'])
        print('title', article['title'])
        print('content', article['content'])
        print('isins', article['isins'])
        print('---')


def pending_orders():
    request_list = Update.RequestList()
    request_list.values.extend([
        Update.Request(option=Update.Option.ORDERS, last_updated=0),
    ])

    update = trading_api.get_update(request_list=request_list)
    update_dict = pb_handler.message_to_dict(message=update)
    orders_df = pd.DataFrame(update_dict['orders']['values'])

    if orders_df.shape[0] == 0:
        print('No pending orders.')
    else:
        print(orders_df)
