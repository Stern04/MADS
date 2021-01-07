import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
%matplotlib inline

from pandas.plotting import register_matplotlib_converters
register_matplotlib_converters()

# Suppress warnings
import warnings
from statsmodels.tools.sm_exceptions import ValueWarning
warnings.simplefilter("ignore", ValueWarning)

# Copy and paste the function you wrote in Assignment 2 Part 1 here and import any libraries necessary
# We have tried a more elegant solution by using
# from ipynb.fs.defs.assignment2_part1 import load_data
# but it doesn't work with the autograder...

def load_data():
    daily_new_cases = None

    covid_df = pd.read_csv('assets/time_series_covid19_confirmed_global.csv')
#     print(covid_df.head())

    #try melting
    covid_melty = pd.melt(covid_df, id_vars = ['Country/Region', 'Province/State'], value_vars = covid_df.columns[4:],
                      var_name = 'Date', value_name = 'Cumulative_Cases')
#     print(covid_melty.tail(5))


    #try to group by date, then later take the diff of each column before...
    covid_groupdate = covid_melty.groupby('Date').sum().reset_index()
#     print(covid_groupdate.head())

    #Create a column that converts every Date string into a pd.DatetimeIndex, then set this as the index and drop the old
    #Date column
    covid_groupdate['Date_Time'] = pd.to_datetime(covid_groupdate['Date'])
    covid_groupdate.sort_values(by='Date_Time',inplace = True)
    covid_groupdate.drop('Date', axis = 1, inplace = True)
    covid_groupdate.set_index('Date_Time', inplace = True)
#     covid_groupdate.head()

    #Take the difference between every day its respective next day.
    #Rename the column to New cases as calculated be .diff()
    #Drop NA rows. The top row after running .diff() is always NA as there was no day before it
    covid_new_cases = covid_groupdate.diff()
    covid_new_cases.rename(columns = {'Cumulative_Cases':'New_Cases'}, inplace=True)
    covid_new_cases.dropna(inplace=True)
#     covid_new_cases


    daily_new_cases = covid_new_cases['New_Cases']


    return daily_new_cases













import math

def calc_rolling_stats(ser, wd_size=7):
    """
    Takes in a series and returns the rolling mean and the rolling std for a window of size wd_size
    """
    # YOUR CODE HERE

    rolling_mean = []
    rolling_std = []

    for j in range(1,len(ser)+1):
        if j < wd_size:
            short_wd = ser[:j]

            #Get rolling mean for window size short_wd
            accum_vals_mean = []

            for i in range(len(short_wd)):
                accum_vals_mean.append(short_wd[i])

            new_val_mean = sum(accum_vals_mean)/len(short_wd)

            rolling_mean.append(new_val_mean)

            #Get rolling std for windown size short_wd
            accum_vals_std = []

            for i in range(len(short_wd)):
                accum_vals_std.append((short_wd[i]-new_val_mean)**2)

            new_val_std = math.sqrt(sum(accum_vals_std)/len(short_wd))

            rolling_std.append(new_val_std)

        else:
            full_wd = ser[j-wd_size:j]

            #Get rolling mean for full window sieze full_wd
            accum_vals_mean = []

            for i in range(len(full_wd)):
                accum_vals_mean.append(full_wd[i])

            new_val_mean = sum(accum_vals_mean)/len(full_wd)

            rolling_mean.append(new_val_mean)

            #Get rolling std for windown size full_wd
            accum_vals_std = []

            for i in range(len(full_wd)):
                accum_vals_std.append((full_wd[i]-new_val_mean)**2)

            new_val_std = math.sqrt(sum(accum_vals_std)/len(full_wd))

            rolling_std.append(new_val_std)

    rolling_mean, rolling_std = np.asarray(rolling_mean), np.asarray(rolling_std)


    return rolling_mean, rolling_std






def calc_log_ret(ser):
    """
    Takes in a series and computes the log return
    """

#     log_ret = ser.apply(lambda x:(np.log(x) - np.log(x - 1)) if x != ser[0])
    log_ret = pd.Series([np.log(ser[i]) - np.log(ser[i-1]) for i in range(1,len(ser))], index = ser.index[1:])
    print(log_ret)
    # YOUR CODE HERE

    return log_ret
