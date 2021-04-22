import degiroapi
from termcolor import colored
from gamestonk_terminal.config_terminal import DG_USERNAME as user, DG_PASSWORD as pw

degiro = degiroapi.DeGiro()


def login():
    degiro.login(user, pw)


def logout():
    degiro.logout()


def show_holdings():
    # Fetch current portfolio
    portfolio = degiro.getdata(degiroapi.Data.Type.PORTFOLIO, True)

    print("")
    print(
        "ProductType\t Stonk\t Size\t last price \t prev close \t breakeven \t % Change"
    )
    print("")

    # Loop to get stock info based on id provided in portfolio
    # showcase portfolio
    for stock in portfolio:
        if stock["positionType"] == "PRODUCT":
            stock_info = degiro.product_info(stock["id"])
            real_time_info = degiro.real_time_price(
                stock["id"], degiroapi.Interval.Type.One_Day
            )
            pos_type = stock_info["productType"]
            size = stock["size"]
            break_even = stock["breakEvenPrice"]
            stonk = stock_info["symbol"]
            last_price = real_time_info[0]["data"]["lastPrice"]
            prev_close = real_time_info[0]["data"]["previousClosePrice"]
            pct_change = round((last_price - prev_close) / prev_close, 3)
            to_pr = f"{pos_type}\t\t {stonk}\t {size}\t {last_price}\t\t {prev_close}\t\t {break_even}\t\t {pct_change}"
            if last_price >= prev_close:
                print(colored(to_pr, "green"))
            else:
                print(colored(to_pr, "red"))
            print("")
