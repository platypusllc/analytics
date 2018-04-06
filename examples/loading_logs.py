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


sensor = "ES2"
channel = 'ec'

for folder in glob.glob('/home/shawn/NL2/nordpolder_van_delfgauw/'):
    print "processing folder: ", folder
    for file in glob.glob(folder+'platypus_20180215_104248.txt'):
        if (os.path.exists(file)):
            print file
            out_name = os.path.basename(os.path.splitext(file)[0])
            print out_name

            data = platypus.io.logs.merge_files(glob.glob(folder+"/*.txt"))
            data = trim_using_EC(data, 100)

            # Access the first 100 GPS locations for the vehicle.
            poses = data['pose']

            output_base = folder+out_name+"_"+channel

            # plt.title("Path of vehicle: " + out_name)
            # # Plot the first 100 GPS locations as UTM coordinates using matplotlib.
            # plt.plot(poses['easting'], poses['northing'])
            # plt.savefig(output_base + "_path.png")
            # plt.show()
            # # plt.clear()

            # Retrieve temperature data from the ES2 sensor.
            # temp = data[sensor]['temp']


            # Plot ES2 electrical conductivity data using matplotlib.

            # print data[sensor][channel]

            plt.title("Graph of "+channel+" data: " + out_name)
            plt.plot(data[sensor].index, data[sensor][channel])
            # plt.savefig(folder+"_"+channel+"_graph.png")
            plt.savefig(output_base + "_graph.png")

            plt.show()
            # plt.clear()

            # Get the standard deviation of the ES2 data.
            es2_stddev = data[sensor].std()
            print "deviation", es2_stddev
