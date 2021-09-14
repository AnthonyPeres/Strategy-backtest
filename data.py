import requests
from bs4 import BeautifulSoup
import pandas as pd
import yfinance as yf

def getData(
    ticker, 
    start_date='2019-01-01',
    end_date='2021-12-31',
    interval='1d',
    drop_columns=True
):
    data = yf.Ticker(ticker=ticker)
    data = data.history(start=start_date, end=end_date, interval=interval)
    if drop_columns:
        data.drop(columns=['Open', 'High', 'Low', 'Volume', 'Dividends', 'Stock Splits'], inplace=True)
    return data


def fetchStockComponents(stock_symbols):
    """
    Récupère la liste des composants pour un indice boursier tel que le CAC40 ('^FCHI' sur yahoo finance)
    Pour l'erreur 404 voir :  https://stackoverflow.com/questions/68259148/getting-404-error-for-certain-stocks-and-pages-on-yahoo-finance-python
    """
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/71.0.3578.98 Safari/537.36',
        'DNT'             : '1',
        'Connection'      : 'close' 
    }

    if type(stock_symbols) == str:
        stock_symbol_tmp = list()
        stock_symbol_tmp.append(stock_symbols)
        stock_symbols = stock_symbol_tmp

    tableau = pd.DataFrame()
    
    for stock_symbol in stock_symbols:    
        url = 'https://finance.yahoo.com/quote/'+ stock_symbol + '/components?p=' + stock_symbol
        r = requests.get(url, headers=headers)

        if not r.status_code == requests.codes.ok:
            raise Exception(f'Réponse code {r.status_code}.')

        if 'lookup' in r.url:
            raise Exception(f'Symbole {stock_symbol} non valide.')

        soup = BeautifulSoup(r.text, 'html.parser')
        table = soup.find('table')
        body = table.find('tbody')
        trs = body.findAll('tr')

        names = []

        for tr in trs:
            name = tr.find('a')
            names.append(name.text)

        tableau[stock_symbol] = pd.Series(names)
        
    return tableau