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
import platypus.io.insitu_logs
import platypus.util.conversions
import glob
import os
import numpy as np
import math

# Read the data log from file.
# Note: for log versions <5.0, this filename must be 'airboat_[timestamp].txt].

def trim_using_EC(dataframe, threshold=100):
    """
    Trims any data when EC < 100
    :return: trimmed dataframe
    """
    if "ES2" in dataframe:
        print("ES2 sensor is present. Trimming all data within EC < {:.0f} time windows\n".format(threshold))
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
        # print(ec_eq_zero_indices)
        # print(windows)
        for window in windows:
            time_window = [ES2_data["ec"].index.values[window[0]], ES2_data["ec"].index.values[window[1]]]
            for k in dataframe:
                dataframe[k] = dataframe[k].loc[np.logical_or(dataframe[k].index < time_window[0], dataframe[k].index > time_window[1])]
    else:
        print("No ES2 sensor present. No trimming will be performed.")
    return dataframe


def load_data(folders = [], files = [], ec_trim_value = 50):
    if (len(folders) == 0):
        folders = [sys.path.cwd]

    # print("folders", str(folders))

    for folder in folders:
        files.extend(glob.glob(folder+'/*fixed*.csv'))

    # print("log files: " + str(files))
    # todo: remove duplicates?

    data = platypus.io.insitu_logs.merge_files(files)
    data = trim_using_EC(data, ec_trim_value)
    return data

def plot_hist_sensor(data, sensor = 'ES2', num_bins = 10, hide_top_n_percent = 0, hide_bot_n_percent = 0, save_dir = "~/save"):
    num_readings = len(data[sensor])
    # Get the std of the data
    sensor_stddev = data[sensor].std()
    # Get the mean of the data
    sensor_mean = data[sensor].mean()
    # Get the min of the data
    sensor_min = data[sensor].min()
    # Get the max of the data
    sensor_max = data[sensor].max()

    print(sensor+" number of readings", num_readings)
    print(sensor+" std", sensor_stddev)
    print(sensor+" mean", sensor_mean)
    print(sensor+" min", sensor_min)
    print(sensor+" max", sensor_max)

    hist_max = math.ceil(sensor_max - hide_top_n_percent * 0.01 * sensor_max)
    hist_min = math.floor(sensor_min + hide_bot_n_percent * 0.01 * sensor_min)
    bin_size = (hist_max - hist_min)/float(num_bins)

    bins = np.arange(hist_min, hist_max, bin_size)
    # print(hist_max, hist_min, bin_size, bins)

    # n, bins, patches = plt.hist(data[sensor], bins=xrange(200,1600,100))
    weights = np.ones_like(data[sensor])/float(num_readings) * 100
    if (num_bins <= 0):
        n, bins, patches = plt.hist(data[sensor], weights=weights)
    else:
        n, bins, patches = plt.hist(data[sensor], weights=weights, bins=bins)

    # print(n, bins, patches)

    plt.xlabel(sensor)
    plt.ylabel('Percentage of values in the given range')
    plt.ylim(0,50)
    plt.title('Histogram of ' + sensor + ' ' + save_dir.split('/')[-1])
    plt.savefig(save_dir + "/"+'Histogram of ' + sensor + ' ' + save_dir.split('/')[-1]+'.png')
    # plt.text(0, .25, "Standard Dev: " + str(es2_stddev))
    plt.figtext(.16, .75, "Mean: " + str(sensor_mean))
    plt.figtext(.16, .7, "std: " + str(sensor_stddev))
    plt.grid(True)
    plt.show()

def get_folders():
    # folders = ['/home/shawn/NL2/grokeneveldse_polder/grokeneveldse_polder_feb_2018/']
    folders = ['/home/shawn/data/june 18 2018 - NL delfgauw/day_1', '/home/shawn/data/june 18 2018 - NL delfgauw/day_2']
    return folders

def main():
    print("enter EC trim value: ")
    new_ec_trim = int(raw_input())

    folders = get_folders()

    data = load_data(folders=folders, ec_trim_value = new_ec_trim)
    print(data)
    print("data columns: ", data.keys)

    num_bins = 10
    hide_bot_n_percent = 10
    hide_top_n_percent = 10
    while ( True ):
        print("what would you like to do?")
        print("0: "+"change number of bins (currently: " +str(num_bins)+")")
        print("1: "+"change percentage of bottom to hide (currently: " +str(hide_bot_n_percent)+")")
        print("2: "+"change percentage of top to hide (currently: " +str(hide_top_n_percent)+")")
        for i,x in enumerate(data.keys()):
            print(i+3, ": plot " + x)

        command = raw_input()

        if (command == '0'):
            break
        elif (command == '1'):
            num_bins = int(command)
        elif (command == '2'):
            hide_bot_n_percent = int(command)
        elif (command == '3'):
            hide_top_n_percent = int(command)
        elif(int(command) < len(data.keys()) ):
            plot_hist_sensor(data, data.keys()[int(command)], num_bins = num_bins, hide_top_n_percent = hide_top_n_percent, hide_bot_n_percent=hide_bot_n_percent, save_dir = folders[0])
        else:
            print(command +" is not valid")

    
if __name__ == '__main__':
    main()
