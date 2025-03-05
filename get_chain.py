from datetime import datetime, timedelta
from alpaca.data.historical.option import OptionHistoricalDataClient
from alpaca.data.requests import (
    OptionChainRequest    
)

api_key = "API KEY"
secret_key = "Secret"
option_historical_data_client = OptionHistoricalDataClient(api_key, secret_key)

def ret_chain(symbol, exp):
    req = OptionChainRequest(
        underlying_symbol = symbol,
        expiration_date= nearest_option_expiration(exp)
    )
    chain = option_historical_data_client.get_option_chain(req)
    return chain

def nearest_option_expiration(input_date):
    if isinstance(input_date, str):
        input_date = datetime.strptime(input_date, "%Y-%m-%d").date()

    year, month = input_date.year, input_date.month
    
    # Find third Friday of the current month
    third_friday = get_third_friday(year, month)
    
    if input_date > third_friday:
        # If input date is past the third Friday, check next month's expiration
        next_month = month + 1 if month < 12 else 1
        next_year = year if month < 12 else year + 1
        next_expiration = get_third_friday(next_year, next_month)
        
        # Compare which expiration is closer
        nearest = third_friday if abs((input_date - third_friday).days) <= abs((input_date - next_expiration).days) else next_expiration
    else:
        # If input date is before or on third Friday, compare with last month's expiration
        prev_month = month - 1 if month > 1 else 12
        prev_year = year if month > 1 else year - 1
        prev_expiration = get_third_friday(prev_year, prev_month)
        
        # Compare which expiration is closer
        nearest = prev_expiration if abs((input_date - prev_expiration).days) <= abs((input_date - third_friday).days) else third_friday
    near = nearest.strftime('%Y-%m-%d')
    return near

def get_third_friday(year, month):
    first_day = datetime(year, month, 1)
    first_friday = first_day + timedelta(days=(4 - first_day.weekday() + 7) % 7)
    third_friday = first_friday + timedelta(weeks=2)
    if third_friday.weekday() != 4:
        third_friday += timedelta(days=(4 - third_friday.weekday() + 7) % 7)
    return third_friday.date()
