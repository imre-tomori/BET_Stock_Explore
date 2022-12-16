#!/usr/bin/env python
# coding: utf-8

# In[1]:


import pandas as pd
import os
from matplotlib import pyplot as pp
from sklearn import linear_model
import numpy as np
import config


# ### Funcions

# In[5]:


def read_local_stock_files():
    stock_data_path = '.\\Stock Data'
    stock_files = os.listdir(stock_data_path)
    df = [pd.read_csv(os.path.join(stock_data_path, stock_files[x])) for x in range(len(stock_files))]
    
    # Rename columns, to be able to reference them

    replacable = (' ', '(', ')')
    replace_with = '_'

    for rep in replacable:
        for category in df:
            category.columns = [column.replace(rep, replace_with) for column in category.columns]
            
    return df


# Set Moving Avarage indicators with pandas window function

def set_MA_indicators(e_stock, MA_lengths):
    for length_key, length in MA_lengths.items():
        e_stock[length_key] = e_stock['Utolsó_ár'].ewm(span=length,adjust=False).mean()
    return e_stock


# Set Linear Regression indicators with sklearn

def set_LR_indicators(e_stock, LR_lengths):
    lm = linear_model.LinearRegression()

    for length_key, length in LR_lengths.items():

        # Display_range: Furthest date where we still have the full range of datapoints.
        # Eg. for LR_89, there is atleast 89 datapoints availale.
        # Go back max 1000 steps, and handle negativ values(timeframe too short for calculation).
        display_range = e_stock.shape[0] - length
        if display_range < 0:
            display_range = 0
        elif display_range > 1000:
            display_range = 1000

        lm_predict_index_curve = np.empty([display_range,1])

        index = [x for x in range(length)]
        s_index = pd.DataFrame(index)

        index = 0
        for base in range(-1,-display_range-1,-1):
            lm_index = lm.fit(s_index,e_stock['Utolsó_ár'][base-length:base])

            # Only predict for the last index
            lm_predict_index_curve[display_range-index-1] = lm_index.predict(s_index[-1:])
            index += 1

        # Reshape and pad the list, so it alligns with the stock data and can be added to the dataframe as a new column.
        e_stock[length_key] = np.pad(np.reshape(lm_predict_index_curve,(display_range,)),(e_stock.shape[0]-display_range,0),constant_values=np.nan)
        
    return e_stock


def set_indicators(e_stock, MA_lengths, LR_lengths):
    set_MA_indicators(e_stock, MA_lengths)
    set_LR_indicators(e_stock, LR_lengths)
    return e_stock


def calc_final_signal(e_stock):
    
    rank_all = e_stock[['Utolsó_ár', 'EMA_0', 'EMA_1', 'LR_0', 'LR_1', 'LR_2']].rank(axis=1)
    rank_all_ind = e_stock[['EMA_0', 'EMA_1', 'LR_0', 'LR_1', 'LR_2']].rank(axis=1)
    rank_LR_EMA = e_stock[['EMA_0', 'EMA_1', 'LR_0']].rank(axis=1)
    
    # Determine if we are outside of calculation range.
    rank_all_ind_buy = rank_all_ind[['LR_0','LR_1','LR_2']] != [1,2,3]
    rank_all_ind_sell = rank_all_ind[['LR_2','LR_1','LR_0']] != [1,2,3]
    
    # Buy signal
    # Price is predicted to raise over LR_89/LR_144/LR_169 and eventually above the EMAs.
    # Initial signal is when price touches LR_89.
    rank_pre_signal_buy = rank_all[['Utolsó_ár','LR_0','LR_1','LR_2']] == [1,2,3,4]
    rank_init_signal_buy = rank_all[['LR_0','Utolsó_ár','LR_1','LR_2']] == [1,2,3,4]

    # Sell signal
    # Price is predicted to fall under LR_89/LR_144/LR_169 and eventually below the EMAs.
    # Initial signal is when price touches LR_89.
    rank_pre_signal_sell = rank_all[['Utolsó_ár','LR_0','LR_1','LR_2']] == [6,5,4,3]
    rank_init_signal_sell = rank_all[['LR_0','Utolsó_ár','LR_1','LR_2']] == [6,5,4,3]

    e_stock['Buy_pre'] = e_stock['Utolsó_ár'][rank_pre_signal_buy.all(axis=1)]
    e_stock['Buy_init'] = e_stock['Utolsó_ár'][rank_init_signal_buy.all(axis=1)]

    e_stock['Sell_pre'] = e_stock['Utolsó_ár'][rank_pre_signal_sell.all(axis=1)]
    e_stock['Sell_init'] = e_stock['Utolsó_ár'][rank_init_signal_sell.all(axis=1)]
    #Entry/Exit point
    #Mark where price enters or exits the "init" state.
    e_stock['Entry_point_sell'] = e_stock['Utolsó_ár'][e_stock['Sell_pre'].shift(1).notna()][e_stock['Sell_init'].notna()]
    e_stock['Entry_point_buy'] = e_stock['Utolsó_ár'][e_stock['Buy_pre'].shift(1).notna()][e_stock['Buy_init'].notna()]

    e_stock['Exit_point_sell'] = e_stock['Utolsó_ár'][e_stock['Sell_init'].shift(1).notna()][e_stock['Sell_pre'].notna()]
    e_stock['Exit_point_buy'] = e_stock['Utolsó_ár'][e_stock['Buy_init'].shift(1).notna()][e_stock['Buy_pre'].notna()]

    # Set index columns
    # We can use the index values later in the calculations
    e_stock.loc[e_stock['Sell_init'].notna(), 'Sell_init_index'] = e_stock.index[e_stock['Sell_init'].notna()]
    e_stock.loc[e_stock['Buy_init'].notna(), 'Buy_init_index'] = e_stock.index[e_stock['Buy_init'].notna()]

    e_stock.loc[e_stock['Entry_point_sell'].notna(), 'Entry_point_sell_index'] = e_stock.index[e_stock['Entry_point_sell'].notna()]
    e_stock.loc[e_stock['Entry_point_buy'].notna(), 'Entry_point_buy_index'] = e_stock.index[e_stock['Entry_point_buy'].notna()]

    e_stock.loc[e_stock['Exit_point_sell'].notna(), 'Exit_point_sell_index'] = e_stock.index[e_stock['Exit_point_sell'].notna()]
    e_stock.loc[e_stock['Exit_point_buy'].notna(), 'Exit_point_buy_index'] = e_stock.index[e_stock['Exit_point_buy'].notna()]

    # Forward fill entry/exit point values so we always now what where the previous points
    e_stock['Entry_point_sell_index'] = e_stock['Entry_point_sell_index'].fillna(method='ffill')
    e_stock['Entry_point_buy_index'] = e_stock['Entry_point_buy_index'].fillna(method='ffill')

    e_stock['Exit_point_sell_index'] = e_stock['Exit_point_sell_index'].fillna(method='ffill')
    e_stock['Exit_point_buy_index'] = e_stock['Exit_point_buy_index'].fillna(method='ffill')

    # Calculate init confirmation
    # There is a delay to confirm the signal, and price needs to reach the pre signal levels.
    confirm_window = 30
    # Init is confirmed when the prices in the range defined by the confirm_window, goes back to pre state.
    # Need to make sure only confirmation included, that happen because of the latest init stage.
    e_stock['Sell_init_confirmed'] = e_stock['Utolsó_ár'][e_stock['Sell_pre'].notna()][e_stock['Sell_init_index'].shift(confirm_window).notna() & (e_stock['Sell_init_index'].shift(confirm_window) > e_stock['Entry_point_sell_index'])]
    e_stock['Buy_init_confirmed'] = e_stock['Utolsó_ár'][e_stock['Buy_pre'].notna()][e_stock['Buy_init_index'].shift(confirm_window).notna() & (e_stock['Buy_init_index'].shift(confirm_window) > e_stock['Entry_point_buy_index'])]
    
    # Set init confirmed index and forward fill, so final signal calculation can use it
    e_stock.loc[e_stock['Sell_init_confirmed'].notna(), 'Sell_init_confirmed_index'] = e_stock.index[e_stock['Sell_init_confirmed'].notna()]
    e_stock.loc[e_stock['Buy_init_confirmed'].notna(), 'Buy_init_confirmed_index'] = e_stock.index[e_stock['Buy_init_confirmed'].notna()]
    # Zero out values outside of calculation range, so forward dill doesn't spill into future signals.
    e_stock.loc[rank_all_ind_sell.all(axis=1), 'Sell_init_confirmed_index'] = 0
    e_stock.loc[rank_all_ind_buy.all(axis=1), 'Buy_init_confirmed_index'] = 0
    e_stock['Sell_init_confirmed_index'] = e_stock['Sell_init_confirmed_index'].fillna(method='ffill')
    e_stock['Buy_init_confirmed_index'] = e_stock['Buy_init_confirmed_index'].fillna(method='ffill')

    # Calculate final buy/sell signal
    # Calculate at an entry point, when there has been a confirmation since the last exit point (after the init state)
    e_stock['Final_signal_sell'] = e_stock['Utolsó_ár'][e_stock['Entry_point_sell'].notna()][e_stock['Sell_init_confirmed_index'] > e_stock['Exit_point_sell_index']]
    e_stock['Final_signal_buy'] = e_stock['Utolsó_ár'][e_stock['Entry_point_buy'].notna()][e_stock['Buy_init_confirmed_index'] > e_stock['Exit_point_buy_index']]

    return e_stock


def visualize_signals(e_stock, lookback_range = config.lookback_range, MA_lengths = config.MA_lengths, LR_lengths = config.LR_lengths):
    
    pp.figure(figsize=[50,20])
    pp.plot(e_stock['Dátum'], e_stock['Utolsó_ár'])
    pp.title(label = e_stock['Név'].unique())
    
    pp.axvline(e_stock['Dátum'][-lookback_range:-lookback_range+1])
    
    #Indicators
    pp.plot(e_stock['Dátum'], e_stock['EMA_0'], label='EMA ' + str(MA_lengths['EMA_0']), color='red')
    pp.plot(e_stock['Dátum'], e_stock['EMA_1'], label='EMA ' + str(MA_lengths['EMA_1']), color='red')
    pp.plot(e_stock['Dátum'], e_stock['LR_0'], label='Linear Regression Curve ' + str(LR_lengths['LR_0']), color='purple')
    pp.plot(e_stock['Dátum'], e_stock['LR_1'], label='Linear Regression Curve ' + str(LR_lengths['LR_1']), color='gold')
    pp.plot(e_stock['Dátum'], e_stock['LR_2'], label='Linear Regression Curve ' + str(LR_lengths['LR_2']), color='brown')
    
    #Buy plot
    pp.plot(e_stock['Dátum'], e_stock['Buy_pre'], label='Buy pre', linestyle = '--', color='#27ae60', linewidth=3)
    pp.plot(e_stock['Dátum'], e_stock['Buy_init'], label='Buy init', color='#1e8449', linewidth=3)
    pp.plot(e_stock['Dátum'], e_stock['Buy_init_confirmed'], 'x', label='Buy init confirmed', color='#1e8449', markersize=15)
    pp.plot(e_stock['Dátum'], e_stock['Final_signal_buy'], '^', label='Final Buy Signal', color='#1e8449', markersize=15)
    
    #Sell plot
    pp.plot(e_stock['Dátum'], e_stock['Sell_pre'], label='Sell pre', linestyle = '--', color='#c0392b', linewidth=3)
    pp.plot(e_stock['Dátum'], e_stock['Sell_init'], label='Sell init', color='#922b21', linewidth=3)
    pp.plot(e_stock['Dátum'], e_stock['Sell_init_confirmed'], 'x', label='Sell init confirmed', color='#922b21', markersize=15)
    pp.plot(e_stock['Dátum'], e_stock['Final_signal_sell'], 'v', label='Final Sell Signal', color='#922b21', markersize=15)
    
    pp.legend()
    pp.grid()
    
def calculate_final_signal_all(MA_lengths = config.MA_lengths, LR_lengths = config.LR_lengths, lookback_range = config.lookback_range):
    
    df = read_local_stock_files()

    stocks_with_final_signal = []
    stocks_with_other_signal = []
    stocks_with_no_recent_signal = []

    for category in df:
        for company in category['Név'].unique():
            example_stock = category[category.Név == company]
            e_stock = example_stock[['Név', 'Dátum', 'Utolsó_ár']][example_stock.Utolsó_ár.notna()].sort_values(by='Dátum')
            e_stock['Dátum'] = pd.to_datetime(e_stock['Dátum'])

            set_indicators(e_stock, MA_lengths, LR_lengths)
            calc_final_signal(e_stock)

            f_stock = e_stock[-lookback_range:]

            if f_stock[['Final_signal_buy', 'Final_signal_sell']].any().any():
                stocks_with_final_signal.append(e_stock)
            elif f_stock[['Buy_pre','Sell_pre', 'Buy_init', 'Sell_init', 'Buy_init_confirmed', 'Sell_init_confirmed']].any().any():
                stocks_with_other_signal.append(e_stock)
            else:
                stocks_with_no_recent_signal.append(e_stock)
                
    return stocks_with_final_signal, stocks_with_other_signal, stocks_with_no_recent_signal

