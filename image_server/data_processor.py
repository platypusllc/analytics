from ipyleaflet import Map, ImageOverlay, Polyline

from sklearn.neighbors import RadiusNeighborsRegressor
import matplotlib
import matplotlib.cm
from matplotlib import pyplot
import numpy as np
import numpy.lib.recfunctions
import scipy
import scipy.interpolate
import pandas
import platypus.io.logs
import os
import glob
import sys

def sensor_id_to_name(id):
    if (id == 0):
        # Select the sensor and the name of the channel for that sensor.
        sensor_name = 'PH_ATLAS'
        sensor_channel = 'ph'
        sensor_units = "pH"
    elif (id == 1):
        sensor_name = 'EC_DECAGON'
        sensor_channel = 'ec'
        sensor_units = 'Electrical Conductivity (uS/cm)'
    elif (id == 2):
        sensor_name = 'T_DECAGON'
        sensor_channel = 'temperature'
        sensor_units = 'Temperature (C)'
    elif (id == 3):
        sensor_name = 'DO_ATLAS'
        sensor_channel = 'do'
        sensor_units = 'Turbidty (NTU)'

    return (sensor_name, sensor_channel, sensor_units)

def generate_overlay(log_file, sensor_id, min_ec):
    # Import the data from the specified logfile

    log_ext = ".txt"

    log_path = "/home/shawn/data/ERM/log_files/"

    if (os.path.exists(log_path + log_file + log_ext) == False):
        print "File doesn't exist: " + log_path + log_file + log_ext
        log_ext = ".txt.incomplete"
        
        if (os.path.exists(log_path + log_file + log_ext) == False):
            print "Error. log does not exist: " + log_path  + log_file + log_ext
            return False

    log_filenames = [
        log_path + log_file + log_ext
    ]



    data = platypus.io.logs.merge_files(log_filenames)

    (sensor_name, sensor_channel, sensor_units) = sensor_id_to_name(sensor_id)

    # Define useful access variables.
    pose = data['pose']
    position = pose[['latitude', 'longitude']]

    data_boundaries = [ [37.755690, -122.381139], [37.757928, -122.380338]]

    if "T_DECAGON" in data:
        print "Temperature sensor is present. Trimming all data where temperature is changing a lot in a given time windows\n"
        # find all time windows where EC is exactly 0

        # print ES2_data
        T_data = data["T_DECAGON"]
        values = T_data["temperature"].values

        dtemp_dt_limit = 0.5/60.0

        # pose_lat_vals = position["latitude"].values
        # pose_lon_vals = position["longitude"].values
        stddevs = []
        zero_indices = []
        for i, x in enumerate(values):
            zero_indices.append(0)
            stddevs.append(0)
            if (i + 60 < len(values)):
                vals = []
                for x in xrange(i, i+60):
                     vals.append(values[x])
                vals = np.array(vals)
                stddev = vals.std()
                stddevs[i] = stddev
                # if (stddev > 0.1):
                #     print "@ i = " + str(i)+", time = " + str(T_data["temperature"].index[i]) + " - std dev: " + str(stddev)

        for i, x in enumerate(stddevs):
            # print i
            if (x > 0.1):
                # print x
                for y in xrange(i, i+60):
                    zero_indices[y] = 1

        # print zero_indices

    #     ec_eq_zero_indices = np.where(values == 0)[0]
        ec_eq_zero_indices = np.where( (np.array(zero_indices) == 1) )[0] # | out_of_bouds_lat | out_of_bouds_lon )[0]
        # print ec_eq_zero_indices
    #     ec_eq_zero_indices = np.where(values < 50)[0]
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
            print "window: " + str(window)
            time_window = [T_data["temperature"].index.values[window[0]], T_data["temperature"].index.values[window[1]]]
            for k in data:
                data[k] = data[k].loc[np.logical_or(data[k].index < time_window[0], data[k].index > time_window[1])]
        print T_data["temperature"].values[np.where( (np.array(zero_indices) ==1) )[0]]
    else:
        print "No ES2 sensor present. No trimming will be performed."

    if "EC_DECAGON" in data:
        print "ES2 sensor is present. Trimming all data within EC = "+str(min_ec)+" time windows\n"
        # find all time windows where EC is exactly 0
        ES2_data = data["EC_DECAGON"]
        values = ES2_data["ec"].values
        # print pose_lat_vals
        # print pose_lon_vals

        # out_of_bouds_lat = (pose_lat_vals < data_boundaries[0][0]) | (pose_lat_vals > data_boundaries[1][0])
        # out_of_bouds_lon = (pose_lon_vals < data_boundaries[0][1]) | (pose_lon_vals > data_boundaries[1][1])

    #     ec_eq_zero_indices = np.where(values == 0)[0]
        ec_eq_zero_indices = np.where( (values < min_ec) )[0] # | out_of_bouds_lat | out_of_bouds_lon )[0]
    #     ec_eq_zero_indices = np.where(values < 50)[0]
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
            for k in data:
                data[k] = data[k].loc[np.logical_or(data[k].index < time_window[0], data[k].index > time_window[1])]
    else:
        print "No ES2 sensor present. No trimming will be performed."


    # print data
    # if "PH_ATLAS" in data:
    #     print "pH sensor is present. Trimming all data within pH < 6 time windows\n"
    #     # find all time windows where pH is less than 6
    #     pH_data = data["PH_ATLAS"]
    #     values = pH_data["ph"].values
    # #     pH_lt_6_indices = np.where( (values < 6) | (values > 8.5))[0]
    #     pH_lt_6_indices = np.where( (values < 6) )[0]
    #     windows = list()
    #     windows.append([pH_lt_6_indices[0]])
    #     left = pH_lt_6_indices[0]
    #     for ii in range(1, pH_lt_6_indices.shape[0]):
    #         i = pH_lt_6_indices[ii]
    #         if i - left > 5:
    #             windows[-1].append(left)
    #             windows.append([i])
    #         left = i
    #     windows[-1].append(pH_lt_6_indices[-1])
    #     for window in windows:
    #         time_window = [pH_data["ph"].index.values[window[0]], pH_data["ph"].index.values[window[1]]]
    #         for k in data:
    #             data[k] = data[k].loc[np.logical_or(data[k].index < time_window[0], data[k].index > time_window[1])]

    # Print the available sensors and channels for this logfile.
    print "Available sensors/channels:"
    for s in data.keys():
        if s == 'pose' or s == 'BATTERY':
            continue
        for c in data[s].dtypes.keys():
            print "  {:s}, {:s}".format(s, str(c))


    # Extract the pose timing and the sensor data of interest.
    pose_times = pose.index.values.astype(np.float64)

    if sensor_name in data:
        sensor = data[sensor_name]
        sensor_times = sensor.index.values.astype(np.float64)

        # Linearly interpolate the position of the sensor at every sample.
        sensor_pose_interpolator = scipy.interpolate.interp1d(pose_times, position,
                                                              axis=0, bounds_error=False)

        # Add the position information back to the sensor data.
        sensor = sensor.join(pandas.DataFrame(sensor_pose_interpolator(sensor_times), sensor.index,
                                              columns=('latitude', 'longitude')))
        
        # Remove columns that have NaN values (no pose information).
        sensor_valid = np.all(np.isfinite(sensor), axis=1)
        sensor = sensor[sensor_valid]

    # Create a trail of the vehicle's path on the map.
    pl = Polyline(locations=position.as_matrix().tolist())
    pl.fill_opacity = 0.0
    pl.weight = 2

    ## Add a data overlay for the map
    data_padding = [0.0000001, 0.0000001]   # degrees lat/lon
    data_resolution = [0.00001, 0.00001] # degrees lat/lon
    data_interpolation_radius = 0.00001 # degrees lat/lon
    data_bounds = [(position.min() - data_padding).tolist(),
                   (position.max() + data_padding).tolist()]

    print position.min()
    print position.max()
    print data_bounds
    print data_resolution

    # Create a rectangular grid of overlay points.
    data_xv, data_yv = np.meshgrid(
        np.arange(data_bounds[1][0], data_bounds[0][0], -data_resolution[0]),
        np.arange(data_bounds[0][1], data_bounds[1][1], data_resolution[1])
    )
    data_shape = data_xv.shape
    data_xy = np.vstack([data_xv.ravel(), data_yv.ravel()]).T

    print data_shape

    print "starting major processing..."
    if sensor_name in data:
        # Create a radial-basis interpolator over the sensor dataset
        # Then, query it at each point of the rectangular grid.
        #from sklearn.neighbors import RadiusNeighborsClassifier
        #data_estimator = RadiusNeighborsClassifier(radius=data_interpolation_radius, outlier_label=np.nan)
        print "creating radius neighbors regressor"
        data_estimator = RadiusNeighborsRegressor(radius=data_interpolation_radius)

        print "running neighbors fit"
        data_estimator.fit(sensor[['latitude','longitude']], sensor[sensor_channel].astype(np.float))
        print "running predict"
        data_zv = data_estimator.predict(data_xy)
        print "running reshape"
        data_zv = data_zv.reshape(data_shape).T

        print "normalizing data"

        # Normalize data from [0, 1)
        data_max = data_zv[np.isfinite(data_zv)].max()
        data_min = data_zv[np.isfinite(data_zv)].min()
        print "Data min = {:f}   Data max = {:f}".format(data_min, data_max)
        NORMALIZER = data_max # 800
        data_zv = (data_zv - data_min) / (NORMALIZER - data_min)


        print "create color map"
        # Update a color map only at the points that have valid values.
        data_rgb = np.zeros((data_shape[0], data_shape[1], 4), dtype=np.uint8)
        data_rgb = matplotlib.cm.jet(data_zv) * 255
        data_rgb[:,:,3] = 255 * np.isfinite(data_zv)

        # Remove any old image files w/ the same name
        old_png_files = glob.glob('./overlay/[overlay, tint, bar].png')
        for old_png_file in old_png_files:
            print "removing file: " + old_png_file
            os.remove(old_png_file)

        out_prefix = log_file + "-"+sensor_name+"-"+str(min_ec)+'-'

        print "creating overlay files"
        png_filename_rgb = './overlay/'+out_prefix+'overlay.png'
        scipy.misc.imsave(png_filename_rgb, data_rgb)

        # Create image overlay that references generated image.
        # makes an image w/ a slight opaque tint to it
        # data_overlay_tint = np.ones((data_shape[0], data_shape[1], 4), dtype=np.uint8) * 50
        # data_overlay_tint_filename = './overlay/'+out_prefix+'tint.png'
        # scipy.misc.imsave(data_overlay_tint_filename, data_overlay_tint)
        
        # data_bounds_tint = [(position.min() - [x * 500 for x in data_padding]).tolist(),
        #                 (position.max() + [x * 500 for x in data_padding]).tolist()]

        # Make a figure and axes with dimensions as desired.
        fig = pyplot.figure(figsize=(15, 3))
        ax1 = fig.add_axes([0.05, 0.80, 0.9, 0.15])
        # Set the colormap and norm to correspond to the data for which
        # the colorbar will be used.        
        cmap = matplotlib.cm.jet
        norm = matplotlib.colors.Normalize(vmin=data_min, vmax=NORMALIZER)
        cb1 = matplotlib.colorbar.ColorbarBase(ax1, cmap=cmap,
                                               norm=norm,
                                               orientation='horizontal')
        cb1.set_label(sensor_units)

        scale_bar_filename = './overlay/'+out_prefix+'bar.png'
        pyplot.savefig(scale_bar_filename)

        pyplot.close('all')

if __name__ == '__main__':
    log_file = sys.argv[1]
    sensor_id = int(sys.argv[2])
    min_ec = int(sys.argv[3])
    generate_overlay(log_file, sensor_id, min_ec)
    # generate_histogram()
