def money_flow_multiplier(Data):
    """
    En entrée : 
    - Un DataFrame avec les colonnes Close Low et High

    En sortie : 
    - Le même DataFrame avec une colonne MFM

    La formule de l'indicateur est : 
    MFM = (((Close - Low) - (High - Close)) / (High - Low)) * 100
    """
    numerateur = ((Data['Close'] - Data['Low']) - (Data['High'] - Data['Close']))
    denominateur = (Data['High'] - Data['Low'])

    for i in range(len(denominateur)):
        if denominateur[i] == 0:
            denominateur[i] = 0.0001

    Data.loc[:, 'MFM'] = (numerateur / denominateur) * 100
    return Data



if __name__ == "__main__":
    import yfinance as yf
    import matplotlib.pyplot as plt
    import datetime

    tick_symbol = input("Ticker Symbol: ")
    str_start_date = input("Start Date (YYYY-MM-DD): ")
    str_end_date = input("End Date (YYYY-MM-DD): ")

    start_date = datetime.datetime.strptime(str_start_date, '%Y-%m-%d')    
    end_date = datetime.datetime.strptime(str_end_date, '%Y-%m-%d')

    # Get data from yfinance
    data = yf.Ticker('AAPL').history(start=start_date, end=end_date)

    # Appli money_flow_multiplier function
    money_flow_multiplier(data)

    # Display head and tail
    print(data.head())
    print(data.tail())

    # PLOT CLOSE AND MFM
    fig = plt.figure(figsize=(20,10))
    ax1 = fig.add_subplot(211)
    ax1.plot(data['Close'], 'black', label='Close')
    ax1.grid(True)
    ax2 = fig.add_subplot(212)
    ax2.plot(data['MFM'], 'r', label='MFM')
    ax2.hlines(y=[90,-90], xmin=start_date, xmax=end_date, colors='g', linestyles='--')
    ax2.grid(True)
    plt.legend()
    plt.show()