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

    stock_info = []
    # Loop to get stock info based on id provided in portfolio
    for stock in portfolio:
        if stock["positionType"] == "PRODUCT":
            stock_info.append(
                degiro.real_time_price(stock["id"], degiroapi.Interval.Type.One_Day)
            )

    # showcase portfolio
    print("")
    print("Stonk\t last price \t prev close \t equity \t % Change")
    print("")
    for info in stock_info:
        stonk = info[0]["data"]["alfa"]
        last_price = info[0]["data"]["lastPrice"]
        prev_close = info[0]["data"]["previousClosePrice"]
        eq = "N/A"
        pct_change = round((last_price - prev_close) / prev_close, 3)
        to_print = f"{stonk}\t {last_price}\t\t {prev_close}\t\t {eq}\t\t {pct_change}"
        if last_price >= prev_close:
            print(colored(to_print, "green"))
        else:
            print(colored(to_print, "red"))
    print("")
