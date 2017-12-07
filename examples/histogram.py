#!/usr/bin/env python
# coding: utf-8

"""
Example of loading Platypus vehicle logs from file.

Data is loaded as time series into Pandas[1] DataFrames, from which they can
be interpolated and filtered for other purposes, or used as input into Numpy[2]
or Scipy[3] functions.

[1]: http://pandas.pydata.org/
[2]: http://www.numpy.org/
[3]: http://www.scipy.org/
"""
import matplotlib.pyplot as plt
import platypus.io.logs
import platypus.util.conversions
import glob
import os
import numpy as np
import plotly.plotly as py

# Read the data log from file.
# Note: for log versions <5.0, this filename must be 'airboat_[timestamp].txt].

def trim_using_EC(dataframe, threshold=100):
    """
    Trims any data when EC < 100
    :return: trimmed dataframe
    """
    if "ES2" in dataframe:
        print "ES2 sensor is present. Trimming all data within EC < {:.0f} time windows\n".format(threshold)
        # find all time windows where EC is exactly 0
        ES2_data = dataframe["ES2"]
        values = ES2_data["ec"].values
        ec_eq_zero_indices = np.where(values < threshold)[0]
        windows = list()
        windows.append([ec_eq_zero_indices[0]])
        left = ec_eq_zero_indices[0]
        for ii in range(1, ec_eq_zero_indices.shape[0]):
            i = ec_eq_zero_indices[ii]
            if i - left > 5:
                # there has been a jump in index, a new time window has started
                windows[-1].append(left)
                windows.append([i])
            left = i
        windows[-1].append(ec_eq_zero_indices[-1])
        # print ec_eq_zero_indices
        # print windows
        for window in windows:
            time_window = [ES2_data["ec"].index.values[window[0]], ES2_data["ec"].index.values[window[1]]]
            for k in dataframe:
                dataframe[k] = dataframe[k].loc[np.logical_or(dataframe[k].index < time_window[0], dataframe[k].index > time_window[1])]
    else:
        print "No ES2 sensor present. No trimming will be performed."
    return dataframe


folders = ['/home/shawn/day4','/home/shawn/day3','/home/shawn/day2','/home/shawn/day1']

for folder in folders:
    data = platypus.io.logs.merge_files(glob.glob(folder+'/*.txt'))
    data = trim_using_EC(data, 200)

    channel = 'ph'
    sensor ='ATLAS_PH'

    # Get the standard deviation of the ES2 data.
    es2_stddev = data[sensor][channel].std()
    print channel +" std", es2_stddev

    # Get the mean of the ES2 data.
    es2_mean = data[sensor][channel].mean()
    print channel+" mean", es2_mean

    # bins = np.arange(6,13,0.5)
    # bins = np.arange(200,1800,100)
    bins = np.arange(5.5, 9 + 0.5, 0.25)
    # n, bins, patches = plt.hist(data[sensor][channel], bins=xrange(200,1600,100))
    n, bins, patches = plt.hist(data[sensor][channel], normed=False, bins=bins)

    print n, bins, patches

    plt.xlabel(channel)
    plt.ylabel('Counts')
    plt.title('Histogram of ' + channel + ' ' + folder.split('/')[-1])
    plt.savefig('Histogram of ' + channel + ' ' + folder.split('/')[-1]+'.png')
    # plt.text(0, .25, "Standard Dev: " + str(es2_stddev))
    plt.figtext(.16, .75, "Mean: " + str(es2_mean))
    plt.figtext(.16, .7, "std: " + str(es2_stddev))
    plt.grid(True)
    plt.show()
