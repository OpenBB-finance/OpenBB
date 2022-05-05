import numpy as np
import math
from scipy.stats import norm

from openbb_terminal.stocks.options import op_helpers
from openbb_terminal.rich_config import console

def calc_hedge(portfolio_option_amount, side, sign):
    portfolio_option_delta = greeks[0][0]
    portfolio_option_gamma = greeks[0][1]
    portfolio_option_vega = greeks[0][2]

    option_a_delta = greeks[1][0]
    option_a_gamma = greeks[1][1]
    option_a_vega = greeks[1][2]

    option_b_delta = greeks[2][0]
    option_b_gamma = greeks[2][1]
    option_b_vega = greeks[2][2]

    delta_multiplier = 1 # Delta will be positive for long call and short put positions, 
    # negative for short call and long put positions.
    
    gamma_multiplier = 1 # Gamma is always positive for long positions 
    # and negative for short positions.
    
    vega_multiplier = 1 # Vega will be positive for long positions 
    # and negative for short positions.

    short = False
    if sign == -1: # Short position
        short = True
        gamma_multiplier = -1
        vega_multiplier = -1
        if side == "call": # Short call position
            delta_multiplier = -1
    elif side == "put":
        if sign == 1: # Long put position
            delta_multiplier = -1


    options_array = np.array([[option_a_gamma, option_b_gamma], [option_a_vega, option_b_vega]])

    portfolio_greeks = [[portfolio_option_gamma*portfolio_option_amount], [portfolio_option_vega*portfolio_option_amount]]

    inv = np.linalg.inv(np.round(options_array, 2))

    w = np.dot(inv, portfolio_greeks)

    portfolio_greeks = [[portfolio_option_delta*delta_multiplier*portfolio_option_amount], 
    [portfolio_option_gamma*gamma_multiplier*portfolio_option_amount], [portfolio_option_vega*vega_multiplier*portfolio_option_amount]]
    options_array = np.array([[option_a_delta, option_b_delta], [option_a_gamma, option_b_gamma], [option_a_vega, option_b_vega]])

    if not short:
        neutral = np.round(np.dot(np.round(options_array, 2), w) - portfolio_greeks)
        # print(neutral) to check that gamma and vega exposure is neutralised
    else:
        neutral = np.round(np.dot(np.round(options_array, 2), w) + portfolio_greeks)
        # print(neutral) to check that gamma and vega exposure is neutralised

    console.print("Neutral Portfolio weights:\n")
    console.print(w[0][0], "of Option A")
    console.print(w[1][0], "of Option B")
    console.print(neutral[0][0], "shares of Underlying Asset\n")
    
option_list = []
type = 0
portfolio_type = 0
greeks = []

def add_hedge_option(price, implied_volatility, strike, days, side):
    delta = calc_delta(price, implied_volatility, strike, days, 0, side)
    gamma = calc_gamma(price, implied_volatility, strike, days, 0)
    vega = calc_vega(price, implied_volatility, strike, days, 0)
    console.print("\nAdded:")
    console.print("Delta:", delta)
    console.print("Gamma:", gamma)
    console.print("Vega:", vega)
    console.print("IV:", implied_volatility)
    console.print("Strike Price:", strike, "\n")

    temp = []
    temp.append(delta)
    temp.append(gamma)
    temp.append(vega)
    greeks.append(temp)

def rmv_hedge_option(index):
    greeks.pop(index)


def add_portfolio_option(price, strike, type, side, days, implied_volatility):

    delta = calc_delta(price, implied_volatility, strike, days, 0, side)
    gamma = calc_gamma(price, implied_volatility, strike, days, 0)
    vega = calc_vega(price, implied_volatility, strike, days, 0)

    temp = []
    temp.append(delta)
    temp.append(gamma)
    temp.append(vega)
    greeks.append(temp)


def calc_delta(asset_price, asset_volatility, strike_price, time_to_expiration, risk_free_rate, side):
    b = math.exp(-risk_free_rate*time_to_expiration)
    x1 = math.log(asset_price/(b*strike_price)) + .5*(asset_volatility*asset_volatility)*time_to_expiration
    x1 = x1/(asset_volatility*(time_to_expiration**.5))
    z1 = norm.cdf(x1)
    if side == 1:
        return z1
    elif side == -1:
        return z1 -1 

def calc_gamma(asset_price, asset_volatility, strike_price, time_to_expiration, risk_free_rate):
    b = math.exp(-risk_free_rate*time_to_expiration)
    x1 = math.log(asset_price/(b*strike_price)) + .5*(asset_volatility*asset_volatility)*time_to_expiration
    x1 = x1/(asset_volatility*(time_to_expiration**.5))
    z1 = norm.cdf(x1)
    z2 = z1/(asset_price*asset_volatility*math.sqrt(time_to_expiration))
    return z2

def calc_vega(asset_price, asset_volatility, strike_price, time_to_expiration, risk_free_rate):
    b = math.exp(-risk_free_rate*time_to_expiration)
    x1 = math.log(asset_price/(b*strike_price)) + .5*(asset_volatility*asset_volatility)*time_to_expiration
    x1 = x1/(asset_volatility*(time_to_expiration**.5))
    z1 = norm.cdf(x1)
    z2 = asset_price*z1*math.sqrt(time_to_expiration)
    return z2/100


# Based on article of Roman Paolucci: https://towardsdatascience.com/algorithmic-portfolio-hedging-9e069aafff5a