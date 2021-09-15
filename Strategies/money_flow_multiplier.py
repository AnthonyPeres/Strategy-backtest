import yfinance as yf
import matplotlib.pyplot as plt
import datetime
import numpy as np
import hvplot.pandas

def money_flow_multiplier(data, make_entry_exit=True):
    """ Utilisation de la stratégie Money Flow Multiplier
    
    La formule de l'indicateur est : 
    MFM = (((Close - Low) - (High - Close)) / (High - Low)) * 100
    """

    numerateur = ((data['Close'] - data['Low']) - (data['High'] - data['Close']))
    denominateur = (data['High'] - data['Low'])

    for i in range(len(denominateur)):
        if denominateur[i] == 0:
            denominateur[i] = 0.0001

    data.loc[:, 'MFM'] = (numerateur / denominateur) * 100

    if make_entry_exit:
        # On crée le signal
        # MFM > 90: -1
        # MFM < -90: 1
        # -90 <= MFM <= 90: 0
        data['Signal'] = np.NaN
        data.loc[data['MFM'] < -90, 'Signal'] = 1 # Achat
        data.loc[data['MFM'] > 90, 'Signal'] = -1 # Vente
        data['Signal'].fillna(method='ffill', inplace=True)

        data['Entree/Sortie'] = data['Signal'].diff() / 2

    # PLOT
    mfm = data['MFM'].hvplot(ylabel='Price in $', width=1000, height=400)
    security_close = data[['Close']].hvplot(line_color='lightgray', ylabel='Price in $', width=1000, height=400)

    if make_entry_exit:
        entry = data[data['Entree/Sortie'] == 1.0]['Close'].hvplot.scatter(color='green', legend=False, ylabel='Price in $', width=1000, height=400)
        exit = data[data['Entree/Sortie'] == -1.0]['Close'].hvplot.scatter(color='red', legend=False, ylabel='Price in $', width=1000, height=400)
        entry_exit_plot = security_close * mfm * entry * exit
    else:
        entry_exit_plot = security_close * mfm
    
    if stock_symbol:
        entry_exit_plot.opts(title=stock_symbol)  
    else:
        entry_exit_plot.opts(xaxis=None)  
    hvplot.show(entry_exit_plot)  


if __name__ == "__main__":
    tick_symbol = input("Ticker Symbol: ")
    str_start_date = input("Start Date (YYYY-MM-DD): ")
    str_end_date = input("End Date (YYYY-MM-DD): ")

    start_date = datetime.datetime.strptime(str_start_date, '%Y-%m-%d')    
    end_date = datetime.datetime.strptime(str_end_date, '%Y-%m-%d')

    # Get data from yfinance
    data = yf.Ticker(tick_symbol).history(start=start_date, end=end_date)

    # Appli money_flow_multiplier function
    money_flow_multiplier(data)

    # Display head and tail
    print(data.head())
    print(data.tail())