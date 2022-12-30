# BET_Stock_Explore

### Description

Program to explore daily stock data with fundamental indicators. Includes a downloader to get data from the Hungarian Stock Exchange. Visualization includes potential entry points to open long or short positions.  

Main packages used:  
    - pandas: to handle the stock data and set up moving average indicators  
    - sklearn: to fit data on a linear regression model  
    - selenium: to automate the download of stock data by simulating a browser  
    - matplotlib: to visualise stock and indicator data  
    
### Usage

Import custom modules:

    import get_BET_data as gbd
    import calculate_final_signal as cfs
    import config

Call download script. By default it runs on the parameters set in the config.py file. It simulates a firefox browser to downloads the files, saves them in the /Stock Data/ folder and returns the number of succesfully downloaded files.

    message = gbd.get_BET_data(delete_current = True)
    print(message)

Call the final calclation function. This reads the donwloaded files and sets up the indicators with lenghts defined in the config.py file. Moving average is set up with the pandas dataframe ewm function, while the linear regression uses the linear model from sklearn. Latter is calculated for every datapoint in the range and collected to create a linear regression curve.

    stocks_with_final_signal, stocks_with_other_signal, stocks_with_no_recent_signal = \
    cfs.calculate_final_signal_all()

Visalize the data.

    for f_stock in stocks_with_final_signal:
        cfs.visualize_signals(f_stock)

### Interpreting result


Visualization includes a legend to understand the colorcoded indicators. Additional signals higlight the price with red/green color, depending if the stock is under or over valued. Red/Green traingles show potential entry points for short/long positions.

![stock_example.png](/stock_example.png)
