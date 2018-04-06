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
import math

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


def load_data(folders = [], files = [], ec_trim_value = 50):
    if (len(folders) == 0):
        folders = [sys.path.cwd]

    for folder in folders:
        files.extend(glob.glob(folder+'/*.txt'))

    print files
    # todo: remove duplicates?

    data = platypus.io.logs.merge_files(files)
    data = trim_using_EC(data, ec_trim_value)
    return data

def plot_hist_sensor(data, sensor = 'ES2', channel='ec', num_bins = 10, hide_top_n_percent = 0, hide_bot_n_percent = 0, save_dir = "~/save"):
    num_readings = len(data[sensor][channel])
    # Get the std of the data
    sensor_stddev = data[sensor][channel].std()
    # Get the mean of the data
    sensor_mean = data[sensor][channel].mean()
    # Get the min of the data
    sensor_min = data[sensor][channel].min()
    # Get the max of the data
    sensor_max = data[sensor][channel].max()

    print channel+" number of readings", num_readings
    print channel+" std", sensor_stddev
    print channel+" mean", sensor_mean
    print channel+" min", sensor_min
    print channel+" max", sensor_max

    hist_max = math.ceil(sensor_max - hide_top_n_percent * 0.01 * sensor_max)
    hist_min = math.floor(sensor_min + hide_bot_n_percent * 0.01 * sensor_min)
    bin_size = (hist_max - hist_min)/float(num_bins)

    bins = np.arange(hist_min, hist_max, bin_size)
    # print hist_max, hist_min, bin_size, bins

    # n, bins, patches = plt.hist(data[sensor][channel], bins=xrange(200,1600,100))
    weights = np.ones_like(data[sensor][channel])/float(num_readings) * 100
    if (num_bins <= 0):
        n, bins, patches = plt.hist(data[sensor][channel], weights=weights)
    else:
        n, bins, patches = plt.hist(data[sensor][channel], weights=weights, bins=bins)

    # print n, bins, patches

    plt.xlabel(channel)
    plt.ylabel('Percentage of values in the given range')
    plt.ylim(0,50)
    plt.title('Histogram of ' + channel + ' ' + save_dir.split('/')[-1])
    plt.savefig(save_dir + "/"+'Histogram of ' + channel + ' ' + save_dir.split('/')[-1]+'.png')
    # plt.text(0, .25, "Standard Dev: " + str(es2_stddev))
    plt.figtext(.16, .75, "Mean: " + str(sensor_mean))
    plt.figtext(.16, .7, "std: " + str(sensor_stddev))
    plt.grid(True)
    plt.show()

def get_folders():
    # folders = ['/home/shawn/NL2/grokeneveldse_polder/grokeneveldse_polder_feb_2018/']
    folders = ['/home/shawn/NL1/all_nov_2017']
    return folders

def main():
    print "enter EC trim value: "
    new_ec_trim = int(raw_input())

    folders = get_folders()

    data = load_data(folders=folders, ec_trim_value = new_ec_trim)
    while ( True ):
        print "what would you like to do?\n0: quit\n1: plot EC\n2: plot pH\n3: plot DO\n4: plot temp\n5: change EC trim value"
        command = raw_input()

        if (command == '0'):
            break
        elif (command == '1'):
            plot_hist_sensor(data, 'ES2', 'ec', num_bins = 10, hide_top_n_percent = 0, save_dir = folders[0])
        elif (command == '2'):
            plot_hist_sensor(data, 'ATLAS_PH', 'ph', num_bins = 10, hide_bot_n_percent = 0, save_dir = folders[0])
        elif (command == '3'):
            plot_hist_sensor(data, 'ATLAS_DO', 'do', num_bins = 10, save_dir = folders[0])
        elif (command == '4'):
            plot_hist_sensor(data, 'ES2', 'temperature', num_bins = 10, save_dir = folders[0])
        else:
            print command +" is not valid"

    
if __name__ == '__main__':
    main()
