import pandas as pd
import numpy as np

def application_strategie(data, capital_initial=100000, taille_lot=500):
    """
    Génère un tableau global des opérations d'achat et de vente en faisant apparaitre 
    les flux de monnaie et de titre a partir d'un dataFrame contenant le cour de l'action, 
    le signal de presence sur le marché et le momentum d'entree et de sortie,

    PARAMETRES
    - data: Le DataFrame contenant au minimum une colonne Close, une colonne Signal et une colonne Entree/Sortie
    - capital_initial: Le capital initial du compte
    - taille_lot: La taille des lots en action

    SORTIE
    Le dataFrame en sortie contient les colonnes : 
    """
    
    if not {'Close', 'Signal', 'Entree/Sortie'}.issubset(data.columns):
        raise Exception('Colonne(s) Close, Signal et/ou Entree/Sortie manquante(s) dans le DataFrame.')
    
    data['Nombre de titres detenus'] = data['Signal'] * taille_lot
    data['Nombre achat/vente'] = data['Entree/Sortie'] * taille_lot
    data['Valeur titres detenus'] = data['Close'] * data['Nombre achat/vente'].cumsum()
    data['Espece disponible'] = capital_initial - (data['Close'] * data['Nombre achat/vente']).cumsum()
    data['Valeur totale du portefeuille'] = data['Valeur titres detenus'] + data['Espece disponible']
    data['Rendement quotidient'] = data['Valeur totale du portefeuille'].pct_change()
    data['Rendement cumules'] = (1 + data['Rendement quotidient']).cumprod() - 1



def synthese_portfolio(data, nb_jours_bourse=252):
    """
    Retourne un DataFrame contenant plusieurs indicateurs en relation avec le portefeuille.
    - 1. Rendement cumulé       — retour sur investissement total.
    - 2. Rendement annuel       — retour sur investissement reçu cette année-là.
    - 3. Volatilité annuelle    — volatilité quotidienne multipliée par la racine carrée de 252 jours de bourse.
    - 4. Ratio de Sharpe        — mesure la performance d'un investissement par rapport à un actif sans risque, après ajustement pour son risque.
    - 5. Ratio de Sortino       — différencie la volatilité nuisible de la volatilité globale totale en utilisant l'écart type de l'actif des 
                                  rendements négatifs du portefeuille, l'écart à la baisse, au lieu de l'écart type total des rendements du portefeuille.
    """

    if not {'Rendement quotidient', 'Rendement cumules'}.issubset(data.columns):
        raise Exception('Colonne(s) Rendement quotidient et/ou Rendement cumules manquante(s) dans le DataFrame.')

    # Creation du DataFrame
    indicateurs = [
        'Rendements cumulés',
        'Rendements annuels',
        'Volatilité annuelle',
        'Ratio de Sharpe',
        'Ratio de Sortino'
    ]
    columns = ['Backtest']
    synthese_portfolio_df = pd.DataFrame(index=indicateurs, columns=columns)
    
    # Calcul des indicateurs
    synthese_portfolio_df.loc['Rendements cumulés'] = data['Rendement cumules'][-1]
    synthese_portfolio_df.loc['Rendements annuels'] = (data['Rendement quotidient'].mean() * nb_jours_bourse)
    synthese_portfolio_df.loc['Volatilité annuelle'] = (data['Rendement quotidient'].std() * np.sqrt(nb_jours_bourse))
    synthese_portfolio_df.loc['Ratio de Sharpe'] = (data['Rendement quotidient'].mean() * nb_jours_bourse) / (data['Rendement quotidient'].std() * np.sqrt(nb_jours_bourse)) # Voir si on peut pas faire rendements / volatilité annuelle

    # (Ratio de Sortino)
    ratio_sortino_df = data[['Rendement quotidient']].copy()
    ratio_sortino_df.loc[:, 'Retours baissiers'] = 0
    cible = 0
    mask = ratio_sortino_df['Rendement quotidient'] < cible
    ratio_sortino_df.loc[mask, 'Retours baissiers'] = ratio_sortino_df['Rendement quotidient']**2
    baisse_stdev = np.sqrt(ratio_sortino_df['Retours baissiers'].mean()) * np.sqrt(nb_jours_bourse)
    expected_return = ratio_sortino_df['Rendement quotidient'].mean() * nb_jours_bourse
    ratio_sortino = expected_return / baisse_stdev

    synthese_portfolio_df.loc['Ratio de Sortino'] = ratio_sortino
    
    return synthese_portfolio_df


def synthese_trade(data, symbole):
    """
    - Faites une boucle dans DataFrame, si le commerce « Entrée / Sortie » est égal à 1, définissez les métriques du commerce d'entrée.
    - Si « Entrée/Sortie » est égal à -1, définissez les métriques de commerce de sortie et calculez le profit.
    - Ajouter l'enregistrement à l'évaluation commerciale DataFrame.
    """

    if not {'Entree/Sortie', 'Valeur titres detenus', 'Nombre achat/vente', 'Close'}.issubset(data.columns):
        raise Exception('Une ou plusieurs colonnes manquante(s) dans le DataFrame.')

    synthese_trade_df = pd.DataFrame(
        columns=[
            'Symbole', 
            'Date d\'entree', 
            'Date de sortie', 
            'Nombre d\'actions', 
            'Prix achat d\'une action', 
            'Prix de vente d\'une action', 
            'Valeur totale des actions a l\'achat', 
            'Valeur totale des actions a la vente', 
            'Gain/Perte'
        ]
    )

    date_entree = date_sortie = ''
    valeurs_actions_achat = valeurs_actions_vente = nb_actions = prix_achat = prix_vente = 0

    # On boucle a travers le DataFrame, si Entree/Sortie = 1, on défini l'achat, sinon si Entree/Sortie = -1 on sort de l'achat et on calcule le profit
    for index, row in data.iterrows():
        if row['Entree/Sortie'] == 1:
            date_entree = index 
            valeurs_actions_achat = abs(row['Valeur titres detenus'])
            nb_actions = row['Nombre achat/vente']
            prix_achat = row['Close']
        
        elif row['Entree/Sortie'] == -1:
            date_sortie = index
            valeurs_actions_vente = abs(row['Close'] * row['Nombre achat/vente'])
            prix_vente = row['Close']
            gain_perte = valeurs_actions_vente - valeurs_actions_achat

            # On crée la ligne de l'opération
            synthese_trade_df = synthese_trade_df.append(
                {
                    'Symbole': symbole,
                    'Date d\'entree': date_entree,
                    'Date de sortie': date_sortie,
                    'Nombre d\'actions': nb_actions,
                    'Prix achat d\'une action':  prix_achat,
                    'Prix de vente d\'une action': prix_vente,
                    'Valeur totale des actions a l\'achat': valeurs_actions_achat,
                    'Valeur totale des actions a la vente': valeurs_actions_vente,
                    'Gain/Perte': gain_perte
                }, ignore_index=True
            )

    return synthese_trade_df