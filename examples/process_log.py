import os
import sys
import uuid
import matplotlib.cm
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import scipy

from mpl_toolkits.basemap import Basemap, cm
from itertools import groupby
from datetime import datetime

from scipy.interpolate import interp1d
from sklearn.neighbors import RadiusNeighborsRegressor

import numpy.lib.recfunctions

import platypus.io.logs
import platypus.util.conversions as util


min_EC_threshold = 10.0

logFile = os.path.abspath(sys.argv[1])
dataset = platypus.io.logs.load(logFile)


if "ATLAS_PH" in dataset:
	values = dataset["ATLAS_PH"]["ph"].values
	timestamps = dataset["ATLAS_PH"]["ph"].index.values

	settling_index = np.argmax(values > 7.0)
	settling_time = util.convert_timestamp(timestamps[settling_index])
	end_time = util.convert_timestamp(timestamps[-1])


	# Trim all ec data while temperature is settling
	data = dataset["ATLAS_PH"]
	dataset["ATLAS_PH"] = data.ix[data.index.indexer_between_time(settling_time, end_time)]

if "ATLAS_DO" in dataset:
	values = dataset["ATLAS_DO"]["do"].values
	timestamps = dataset["ATLAS_DO"]["do"].index.values
	median_value = np.median(values)

	settling_index = np.argmax(values < median_value)
	settling_time = util.convert_timestamp(timestamps[settling_index])
	end_time = util.convert_timestamp(timestamps[-1])


	# Trim all ec data while temperature is settling
	data = dataset["ATLAS_DO"]
	dataset["ATLAS_DO"] = data.ix[data.index.indexer_between_time(settling_time, end_time)]



# If ES2 data is present, trim all data while ec reading is less than min_EC_threshold
if "ES2" in dataset:
	values = dataset["ES2"]["ec"].values
	timestamps = dataset["ES2"]["ec"].index.values
	
	ec_non_zero_indices = np.where(values > min_EC_threshold)[0]
	
	# Compute time ranges during which ec has values over threshold
	valid_time_ranges = []
	for k, g in groupby(enumerate(ec_non_zero_indices), lambda x: x[0]-x[1]):
		group = list(g)
		start_time = util.convert_timestamp(timestamps[group[0][1]])
		end_time = util.convert_timestamp(timestamps[group[-1][1]])

		valid_time_ranges.append((start_time, end_time))

	# Trim all collected sensor data to lie within the computed time ranges
	for sensor, data in dataset.items():
		valid_data_ranges = [data.ix[data.index.indexer_between_time(start, end)] for start, end in valid_time_ranges]
		dataset[sensor] = pd.concat(valid_data_ranges)

	# Trim all EC values while temperature still settling
	values = dataset["ES2"]["temperature"].values
	timestamps = dataset["ES2"]["temperature"].index.values
	median_value = np.median(values)
	
	settling_index = np.argmax(values < median_value)
	settling_time = util.convert_timestamp(timestamps[settling_index])
	end_time = util.convert_timestamp(timestamps[-1])


	# Trim all ec data while temperature is settling
	data = dataset["ES2"]
	dataset["ES2"] = data.ix[data.index.indexer_between_time(settling_time, end_time)]


# Define useful access variables.
pose = dataset['pose']
position = pose[['latitude', 'longitude']]

print(pose.head())

# Print the available sensors and channels for this logfile.
print("Available sensors/channels:")
for s in dataset.keys():
	if s == 'pose' or s == 'BATTERY':
		continue
	for c in dataset[s].dtypes.keys():
		print(f"{s}, {str(c)}")

# Select the sensor and the name of the channel for that sensor.
sensor_name = 'ATLAS_DO'
sensor_channel = 'do'
#sensor_units = 'Electrical Conductivity (uS/cm)'
#sensor_units = 'Temperature (C)'
sensor_units = 'Dissolved Oxygen (mg/L)'
#sensor_units = 'pH'
# Extract the pose timing and the sensor data of interest.
pose_times = pose.index.values.astype(np.float64)

sensor = dataset[sensor_name]
sensor_times = sensor.index.values.astype(np.float64)

# Linearly interpolate the position of the sensor at every sample.
sensor_pose_interpolator = interp1d(pose_times, pose[['latitude', 'longitude']], axis=0, bounds_error=False)

# Add the position information back to the sensor data.
sensor = sensor.join(pd.DataFrame(sensor_pose_interpolator(sensor_times), sensor.index, columns=('latitude', 'longitude')))

# Remove columns that have NaN values (no pose information).
sensor_valid = np.all(np.isfinite(sensor), axis=1)
sensor = sensor[sensor_valid]

# Add a data overlay for the map
data_padding = [0.0001, 0.0001]   # degrees lat/lon
data_resolution = [0.00001, 0.00001] # degrees lat/lon
data_interpolation_radius = 0.00005 # degrees lat/lon
data_bounds = [(position.min() - data_padding).tolist(), (position.max() + data_padding).tolist()]

# Create a rectangular grid of overlay points.
data_xv, data_yv = np.meshgrid(
	np.arange(data_bounds[1][0], data_bounds[0][0], -data_resolution[0]),
	np.arange(data_bounds[0][1], data_bounds[1][1], data_resolution[1])
)
data_shape = data_xv.shape
data_xy = np.vstack([data_xv.ravel(), data_yv.ravel()]).T

# Create a radial-basis interpolator over the sensor dataset
# Then, query it at each point of the rectangular grid.
#from sklearn.neighbors import RadiusNeighborsClassifier
#data_estimator = RadiusNeighborsClassifier(radius=data_interpolation_radius, outlier_label=np.nan)
data_estimator = RadiusNeighborsRegressor(radius=data_interpolation_radius)

data_estimator.fit(sensor[['latitude','longitude']], sensor[sensor_channel].astype(np.float))
data_zv = data_estimator.predict(data_xy)
data_zv = data_zv.reshape(data_shape).T
data_z = data_zv

# Normalize data from [0, 1)
data_max = data_zv[np.isfinite(data_zv)].max()
data_min = data_zv[np.isfinite(data_zv)].min()
data_zv = (data_zv - data_min) / (data_max - data_min)

# Update a color map only at the points that have valid values.
data_rgb = np.zeros((data_shape[0], data_shape[1], 4), dtype=np.uint8)
data_rgb = matplotlib.cm.jet(data_zv)*255.0
data_rgb[:,:,3] = 255 * np.isfinite(data_zv)


# Make a figure and axes with dimensions as desired.
fig = plt.figure(figsize=(12, 9))
ax1 = fig.add_axes([0.1,0.1,0.8,0.8])
# Bogota Aqueduct data
loncorners = (-74.0687, -74.0654)
latcorners = (4.70215, 4.70421)
# Oxy data
#loncorners = (-71.090914, -71.075914)
#latcorners = (6.950289, 6.964289)

m = Basemap(projection='robinson', llcrnrlat=latcorners[0],urcrnrlat=latcorners[1],
			llcrnrlon=loncorners[0],urcrnrlon=loncorners[1],
			resolution='i', epsg=3116)

m.arcgisimage(service='World_Imagery', xpixels = 1500, verbose= True, dpi=300)

# draw coastlines, state and country boundaries, edge of map.
m.drawcoastlines()
m.drawstates()
m.drawcountries()

# draw meridians
meridians = np.linspace(loncorners[0],loncorners[1],7)
m.drawmeridians(meridians, labels=[0,0,0,1], fontsize=10, color='w', linewidth=0.3)
#m.drawmapboundary()
# draw parallels.
parallels = np.linspace(latcorners[0],latcorners[1],7)
m.drawparallels(parallels, labels=[1,0,0,0], fontsize=10, color='w', linewidth=0.3)

#print(np.shape(data_xv), np.shape(data_yv), np.shape(data_z))

x, y = m(data_yv.T, data_xv.T) # compute map proj coordinates.
# draw filled contours.
#clevs = [0,1,2.5,5,7.5,10,15,20,30,40,50,70,100,150,200,250,300,400,500,600,750]
cs = m.contourf(x, y, data_z, 30, cmap=matplotlib.cm.nipy_spectral)

# add colorbar.
cbar = m.colorbar(cs,location='bottom',pad="5%")
cbar.set_label(sensor_units)

plt.show()
#plt.pause(5)
fig.savefig(f"{sensor_name}_{sensor_channel}_plot.pdf", dpi=300, bbox_inches='tight')

