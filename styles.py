import pandas as pd 
import numpy as np


def straddle(data, strike):
    call_option = data[(data['strike_price'] == strike) & (data['option_type'] == 'C')].iloc[0]
    put_option = data[(data['strike_price'] == strike) & (data['option_type'] == 'P')].iloc[0]

    straddle_price = call_option['ask_price'] + put_option['ask_price']

    stock_prices = np.linspace(strike - 60, strike + 60, 200)

    call_payoff = np.maximum(stock_prices - strike, 0) - call_option['ask_price']
    put_payoff = np.maximum(strike - stock_prices, 0) - put_option['ask_price']

    straddle_payoff = call_payoff + put_payoff

    return straddle_price, straddle_payoff, stock_prices

def butterfly_spread(data, middle_strike, type):
    
    data_sub = data.loc[data['option_type'] == type]

    lower_strikes = data_sub[data_sub["strike_price"] < middle_strike]["strike_price"]
    upper_strikes = data_sub[data_sub["strike_price"] > middle_strike]["strike_price"]

    if lower_strikes.empty or upper_strikes.empty:
        raise("No valid butterfly spreads")

    lower_strike = lower_strikes.iloc[-1]  # Closest lower strike
    upper_strike = upper_strikes.iloc[0]  # Closest upper strike

    lower_option = data_sub[data_sub["strike_price"] == lower_strike].iloc[0]
    upper_option = data_sub[data_sub["strike_price"] == upper_strike].iloc[0]
    middle_option = data_sub[data_sub["strike_price"] == middle_strike].iloc[0]
    
    K1, K2, K3 = lower_strike, middle_strike, upper_strike
    
    P1, P2, P3 = lower_option['ask_price'], middle_option['bid_price'], upper_option['ask_price']  # Premiums paid/received for each leg

    #Weights in case of non-equidistant strike prices
    w1 = (K3 - K2) / (K3 - K1)
    w2 = -1
    w3 = 1 - w1

    stock_prices = np.linspace(middle_strike - 60, middle_strike + 60, 200)

    # Calculate individual option payoffs
    if type == "C":
        lower_leg = w1 * (np.maximum(stock_prices - K1, 0) - P1)  # Long Call
        middle_leg = w2 * (np.maximum(stock_prices - K2, 0) - P2)  # Short 2 Calls
        upper_leg = w3 * (np.maximum(stock_prices - K3, 0) - P3)  # Long Call

    elif type == "P":
        lower_leg = w1 * (np.maximum(K1-stock_prices, 0) - P1)  # Long Put
        middle_leg = w2 * (np.maximum(K2 - stock_prices, 0) - P2)  # Short 2 Puts
        upper_leg = w3 * (np.maximum(K3 - stock_prices, 0) - P3)  # Long Put

    # Total Butterfly Payoff
    total_payoff = lower_leg + middle_leg + upper_leg

    total_price = w1*P1 + w2*P2 + w3*P3
    
    return total_price, total_payoff, stock_prices

def bull_or_bear(data, bear_or_bull, type, strike_low, strike_high):

    data_sub = data.loc[data['option_type'] == type]

    lower_option = data_sub[data_sub['strike_price'] == strike_low].iloc[0]
    upper_option = data_sub[data_sub['strike_price'] == strike_high].iloc[0]

    stock_prices = np.linspace(strike_low - 60, strike_high + 60, 200)

    if bear_or_bull == "bull":

        total_price = lower_option['ask_price'] - upper_option['bid_price']

        if type == "C":
            low_call_payoff = np.maximum(stock_prices - strike_low, 0) - lower_option['ask_price']
            high_call_payoff = upper_option['bid_price'] - np.maximum(stock_prices - strike_high, 0)

            total_payoff = low_call_payoff + high_call_payoff
        
        elif type == "P":
            low_put_payoff = np.maximum(strike_low - stock_prices, 0) - lower_option['ask_price']
            high_put_payoff = upper_option['bid_price'] - np.maximum(strike_high - stock_prices, 0)

            total_payoff = low_put_payoff + high_put_payoff

    elif type == "bear":
        
        total_price = upper_option['ask_price'] - lower_option['bid_price']

        if type == "C":
            low_call_payoff =  lower_option['bid_price'] - np.maximum(stock_prices - strike_low, 0)
            high_call_payoff = np.maximum(stock_prices - strike_high, 0) - upper_option['ask_price']

            total_payoff = low_call_payoff + high_call_payoff
        
        elif type == "P":
            low_put_payoff =  lower_option['bid_price'] - np.maximum(strike_low - stock_prices, 0)
            high_put_payoff =  np.maximum(strike_high - stock_prices, 0) - upper_option['ask_price']

            total_payoff = low_put_payoff + high_put_payoff

    else:
        raise("Error: make sure strikes are eligible, bear_or_bull formatted as 'bull' or 'bear', and type formatted as 'C' or 'P'.")

    return total_price, total_payoff, stock_prices