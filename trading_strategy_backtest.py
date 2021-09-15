import numpy as np
import pandas as pd 
import hvplot.pandas
import datetime

from data import getData, fetchStockComponents
from backtest import application_strategie, synthese_portfolio, synthese_trade
from Strategies.moving_averages import sma
from Strategies.money_flow_multiplier import money_flow_multiplier 


def calculate_strategy(
    stock_symbol, 
    strategy='sma', 
    start_date='2017-01-01', 
    end_date='2021-01-01', 
    initial_capital=1000, 
    lot_size=10, 
    export_csv=True
    ):
    
    data = getData(stock_symbol, start_date, end_date)
    
    # TODO: Faire en sorte que si le symbol n'est pas trouvé (donc pas de dataframe), exception ou juste print

    if strategy == 'sma':
        days_for_short_sma = 50
        days_for_long_sma = 100
        sma(stock_symbol, data, short_window=days_for_short_sma, long_window=days_for_long_sma, make_entry_exit=True)
    elif strategy == 'mfm':
        money_flow_multiplier(data, make_entry_exit=True)
    else:
        raise Exception('La stratégie passée en paramètre n\'est pas connue.')
    
    application_strategie(data, capital_initial=initial_capital, taille_lot=lot_size)
    portfolio_evaluation_df = synthese_portfolio(data)
    synthese_df = synthese_trade(data, stock_symbol)

    if export_csv == True:
        now = str(datetime.datetime.now())
        data.to_csv(f'./Data/tests/export_resultat_{stock_symbol}_{now}.csv', index=True)

    print(data.tail(10))
    print(portfolio_evaluation_df)
    print(synthese_df)




def calculate_strategy_for_multiples_stocks(stock_symbols):
    components = fetchStockComponents(stock_symbols)
    for stock in components[stock_symbols].values:
        ## Appliquer le backtest sur la value stock
        print(stock)
        # calculate_strategy(stock, export_csv=False)



if __name__ == "__main__":
    symbol = input("Ticker Symbol : ")
    start_date = input("Start Date (YYYY-MM-DD) : ")
    end_date = input("End Date (YYYY-MM-DD) : ")
    capital_initial = int(input('Capital initial : '))
    taille_lot = int(input('Taille_lot : '))
    export_csv = bool(input('Exporter en CSV l\'historique ? : '))

    calculate_strategy(symbol, 'sma', start_date, end_date, capital_initial, taille_lot, export_csv)