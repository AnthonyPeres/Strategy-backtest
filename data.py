def getData(
    ticker, 
    start_date='2019-01-01',
    end_date='2021-12-31',
    interval='1d',
    drop_columns=True
):
    import yfinance as yf
    import pandas as pd

    data = yf.Ticker(ticker=ticker)
    data = data.history(start=start_date, end=end_date, interval=interval)
    if drop_columns:
        data.drop(columns=['Open', 'High', 'Low', 'Volume', 'Dividends', 'Stock Splits'], inplace=True)
    return data
