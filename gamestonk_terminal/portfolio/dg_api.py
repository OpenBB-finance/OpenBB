import degiroapi
from termcolor import colored
from gamestonk_terminal.config_terminal import DG_USERNAME as user, DG_PASSWORD as pw

degiro = degiroapi.DeGiro()


def login():
    while True:
        login_prefr = input("Do you have 2FA activated? - y/n> ")
        if login_prefr == "q":
            break
        elif login_prefr == "y":
            topt = input("Enter TOPT> ")
            degiro.login(user, pw, topt)
            break
        elif login_prefr == "n":
            degiro.login(user, pw)
            break
        else:
            print("Invalid input. Try again.")
            input("Press enter to continue...")


def logout():
    degiro.logout()


def show_holdings():
    # Fetch current portfolio
    portfolio = degiro.getdata(degiroapi.Data.Type.PORTFOLIO, True)

    print("")
    print(
        "PositionType\t Stonk\t Size\t last price \t prev close \t breakeven \t % Change"
    )
    print("")

    # Loop to get stock info based on id provided in portfolio
    # showcase portfolio
    for stock in portfolio:
        if stock["positionType"] == "PRODUCT":
            pos_type = stock["positionType"]
            size = stock["size"]
            break_even = stock["breakEvenPrice"]
            real_time_info = degiro.real_time_price(
                stock["id"], degiroapi.Interval.Type.One_Day
            )
            stonk = real_time_info[0]["data"]["alfa"]
            last_price = real_time_info[0]["data"]["lastPrice"]
            prev_close = real_time_info[0]["data"]["previousClosePrice"]
            pct_change = round((last_price - prev_close) / prev_close, 3)

            to_pr = f"{pos_type}\t\t {stonk}\t {size}\t {last_price}\t\t {prev_close}\t\t {break_even}\t\t {pct_change}"
            if last_price >= prev_close:
                print(colored(to_pr, "green"))
            else:
                print(colored(to_pr, "red"))
            print("")
