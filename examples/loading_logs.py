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

# Read the data log from file.
# Note: for log versions <5.0, this filename must be 'airboat_[timestamp].txt].
data = platypus.io.logs.load('./airboat_20130807_063622.txt')


# Access the first 100 GPS locations for the vehicle.
poses = data['pose'][100:]

# Plot the first 100 GPS locations as UTM coordinates using matplotlib.
plt.plot(poses['easting'], poses['northing'])
plt.show()

# Retrieve temperature data from the ES2 sensor.
temp = data['es2']['temperature']


# Plot ES2 electrical conductivity data using matplotlib.
plt.plot(data['es2'].index, data['es2']['ec'])
plt.show()

# Get the standard deviation of the ES2 data.
es2_stddev = data['es2'].std()
