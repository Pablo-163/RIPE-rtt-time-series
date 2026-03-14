from statsmodels.tsa.stattools import adfuller, kpss
from statsmodels.graphics.tsaplots import plot_acf, plot_pacf
# более мощный тест
from arch.unitroot import PhillipsPerron

import matplotlib.pyplot as plt

def pp_test(ts_array):
    pp = PhillipsPerron(ts_array)
    p_value = pp.pvalue
    if p_value < 0.05:
        text = "Stationary, PP-test "
    else:
        text = "Non-stationary, PP-test"
    return round(p_value, 6), text

def adf_test(ts_array):
    pass

def kpss_test(ts_array):
    pass

def plt_acf_with_text(ts_array, tit='acf', test_func = pp_test):
    
    fig, ax = plt.subplots(figsize=(8, 4))
    plot_acf(ts_array, ax=ax, lags=100)    
    plt.title(tit)
    
    res = test_func(ts_array)
    text = res[1] + 'p-value = '+str(res[0])
    
    plt.legend(['acf'], title=text)
    plt.show()

def plt_pacf_with_text(ts_array, tit='pacf', test_func = pp_test):
    
    fig, ax = plt.subplots(figsize=(8, 4))
    plot_pacf(ts_array, ax=ax, lags=100)
    
    plt.title(tit)
    
    res = test_func(ts_array)
    text = res[1] + 'p-value = '+str(res[0])
    
    plt.legend(['acf'], title=text)
    
    plt.show()

def differentiate_and_correlogram_season(series, windows, test_func = pp_test):
    diff_results = []
    for window in windows:
        differentiated_series = series.diff(window).dropna()
                
        # Plot autocorrelation function
        fig, ax = plt.subplots(figsize=(8, 4))
        plot_pacf(differentiated_series, ax=ax, lags=100)
        plt.title(f'PACF (Window = {window})')

        res = test_func(series)
        diff_results.append((window, res))
        
        text = res[1] + 'p-value = '+str(res[0])
    
        plt.legend(['acf'], title=text)
        
        plt.show()
    return diff_results


def differentiate_and_correlogram(series, orders, test_func = pp_test):
    diff_results = []
    for order in orders:
        differentiated_series = series.diff().dropna()
        result = adfuller(differentiated_series)
        diff_results.append((order, result))
        
        # Plot autocorrelation function
        fig, ax = plt.subplots(figsize=(8, 4))
        plot_pacf(differentiated_series, ax=ax, lags=100)
        plt.title(f'PACF (Order = {order})')

        res = test_func(series)
        text = res[1] + 'p-value = '+str(res[0])
    
        plt.legend(['acf'], title=text)
   
        series = series.diff().dropna()

        plt.show()
    
    return diff_results