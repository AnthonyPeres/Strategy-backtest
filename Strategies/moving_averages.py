def sma(data, short_window=50, long_window=100, make_entry_exit=True):
    """
    Fonction qui calcule les moyennes mobiles arithmétique (non exponentielle) avec
    comme période short_window et long_window sur un DataFrame possédant une colonne 'Close'.

    Si make_entry_exit = True, la fonction va calculer les points d'entrées et de sorties
    en rapport avec la position relative des deux SMA.
    """


    """ 
    Faire une exception si on peut pas faire les 2 sma (taille du df trop courte
    """
    import numpy as np

    # On crée les 2 colonnes SMA[short_window] et SMA[long_window]
    column_short_window = 'SMA' + str(short_window)
    column_long_window = 'SMA' + str(long_window)
    data[column_short_window] = data['Close'].rolling(window=short_window).mean()
    data[column_long_window] = data['Close'].rolling(window=long_window).mean()

    if make_entry_exit:
        # On crée le signal
        # SMA50 < SMA100: 0
        # SMA50 >= SMA100: 1
        data['Signal'] = 0.0
        data['Signal'][short_window:] = np.where(
            data[column_short_window][short_window:] > data[column_long_window][short_window:], 1.0, 0.0
        )

        # On calcul les points d'entrée et de sortie
        # Entry: 1.0
        # Exit: -1.0
        data['Entree/Sortie'] = data['Signal'].diff()


