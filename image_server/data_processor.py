from sklearn.neighbors import RadiusNeighborsRegressor
import matplotlib
matplotlib.use('Agg')

import matplotlib.pyplot as plt
import math
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
import json

log_path = '/home/ubuntu/mount_nas/'

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

def generate_overlay(log_path, log_file, sensor_id, ec_bounds, ph_bounds, turbidity_bounds):
    print "processing: " + log_file
    min_ec = ec_bounds[0]
    max_ec = ec_bounds[1]
    min_ph = ph_bounds[0]
    max_ph = ph_bounds[1]
    min_turbidity = turbidity_bounds[0]
    max_turbidity = turbidity_bounds[1]
    data_padding = [0., 0.]   # degrees lat/lon
    data_resolution = [0.00001, 0.00001] # degrees lat/lon
    data_interpolation_radius = 0.00001 # degrees lat/lon

    data_boundaries = [[37.756664, -122.381500], [37.760387, -122.377216]]

    # read the old generation stats file
    stats_in = {}
    old_stats = {"settings": {}}

    try:
        with open("./stats/"+log_file+'.json', 'r') as infile:
            print "reading previous stats from: " + "./stats/"+log_file+'.json'
            stats_in = json.load(infile)
            print stats_in
            # old_stats = stats_in[str(sensor_id)]
    except:
        print "failed to load from input stats file"

    data_stats = {}
    data_stats["settings"] = {}
    data_stats["settings"]["log_path"] = log_path
    data_stats["settings"]["log_file"] = log_file
    data_stats["settings"]["sensor_id"] = sensor_id
    data_stats["settings"]["ec_bounds"] = ec_bounds
    data_stats["settings"]["ph_bounds"] = ph_bounds
    data_stats["settings"]["turbidity_bounds"] = turbidity_bounds

    print(str(data_stats["settings"]))

    if (data_stats["settings"] == old_stats["settings"]):
        print "old processing settings == new processing settings. don't re-run"
        return

    # Import the data from the specified logfile

    log_ext = ".txt"

    if (os.path.exists(log_path + log_file + log_ext) == False):
        print "File doesn't exist: " + log_path + log_file + log_ext
        log_ext = ".txt.incomplete"
        
        if (os.path.exists(log_path + log_file + log_ext) == False):
            print "Error. log does not exist: " + log_path  + log_file + log_ext
            return False

    data = platypus.io.logs.load(log_path+log_file+log_ext)

    (sensor_name, sensor_channel, sensor_units) = sensor_id_to_name(sensor_id)

    # Define useful access variables.
    if (data_boundaries != []):
        print "Trimming all data within long/lat = "+str(data_boundaries)
        # find all time windows where EC is exactly 0
        ES2_data = data["pose"]
        # print ES2_data["time"]
        values_lat = ES2_data["latitude"].values
        values_lon = ES2_data["longitude"].values

    #     ec_eq_zero_indices = np.where(values == 0)[0]
        lat_min = min(data_boundaries[0][0], data_boundaries[1][0])
        lat_max = max(data_boundaries[0][0], data_boundaries[1][0])
        lon_min = min(data_boundaries[0][1], data_boundaries[1][1])
        lon_max = max(data_boundaries[0][1], data_boundaries[1][1])
        print lat_min, lat_max, " | ", lon_min, lon_max
        ec_eq_zero_indices = np.where( (values_lat < lat_min) | (values_lat > lat_max) |
                                       (values_lon < lon_min) | (values_lon > lon_max)
                                     )[0]
        
        if (len(ec_eq_zero_indices) == 0):
            print "no poses outside the bounds"
        else:
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
                time_window = [ES2_data.index.values[window[0]], ES2_data.index.values[window[1]]]
                # print time_window
                for k in data:
                    print "trimming: " + k +" for interval " + str(time_window)
                    data[k] = data[k].loc[np.logical_or(data[k].index < time_window[0], data[k].index > time_window[1])]


    # if "T_DECAGON" in data:
    #     print "Temperature sensor is present. Trimming all data where temperature is changing a lot in a given time windows\n"
    #     # find all time windows where EC is exactly 0

    #     # print ES2_data
    #     T_data = data["T_DECAGON"]
    #     values = T_data["temperature"].values

    #     dtemp_dt_limit = 0.5/60.0

    #     # pose_lat_vals = position["latitude"].values
    #     # pose_lon_vals = position["longitude"].values
    #     stddevs = []
    #     zero_indices = []
    #     for i, x in enumerate(values):
    #         zero_indices.append(0)
    #         stddevs.append(0)
    #         if (i + 60 < len(values)):
    #             vals = []
    #             for x in xrange(i, i+60):
    #                  vals.append(values[x])
    #             vals = np.array(vals)
    #             stddev = vals.std()
    #             stddevs[i] = stddev
    #             # if (stddev > 0.1):
    #             #     print "@ i = " + str(i)+", time = " + str(T_data["temperature"].index[i]) + " - std dev: " + str(stddev)

    #     for i, x in enumerate(stddevs):
    #         # print i
    #         if (x > 0.1):
    #             # print x
    #             for y in xrange(i, i+60):
    #                 zero_indices[y] = 1

    # #     # print zero_indices

    # #     ec_eq_zero_indices = np.where(values == 0)[0]
    #     ec_eq_zero_indices = np.where( (np.array(zero_indices) == 1) )[0] # | out_of_bouds_lat | out_of_bouds_lon )[0]
    #     # print ec_eq_zero_indices
    # #     ec_eq_zero_indices = np.where(values < 50)[0]
    #     windows = list()
    #     windows.append([ec_eq_zero_indices[0]])
    #     left = ec_eq_zero_indices[0]
    #     for ii in range(1, ec_eq_zero_indices.shape[0]):
    #         i = ec_eq_zero_indices[ii]
    #         if i - left > 5:
    #             # there has been a jump in index, a new time window has started
    #             windows[-1].append(left)
    #             windows.append([i])
    #         left = i
    #     windows[-1].append(ec_eq_zero_indices[-1])
    #     # print ec_eq_zero_indices
    #     # print windows
    #     for window in windows:
    #         print "window: " + str(window)
    #         time_window = [T_data["temperature"].index.values[window[0]], T_data["temperature"].index.values[window[1]]]
    #         for k in data:
    #             data[k] = data[k].loc[np.logical_or(data[k].index < time_window[0], data[k].index > time_window[1])]
    #     print T_data["temperature"].values[np.where( (np.array(zero_indices) ==1) )[0]]
    # else:
    #     print "No ES2 sensor present. No trimming will be performed."

    if "EC_DECAGON" in data:
        print "ES2 sensor is present. Trimming all data within EC = "+str(min_ec)+" time windows\n"
        # find all time windows where EC is exactly 0
        ES2_data = data["EC_DECAGON"]
        values = ES2_data["ec"].values

    #     ec_eq_zero_indices = np.where(values == 0)[0]
        ec_eq_zero_indices = np.where( (values < min_ec) | (values > max_ec) )[0] # | out_of_bouds_lat | out_of_bouds_lon )[0]
        if (len(ec_eq_zero_indices) == 0):
            print "no ec data to trim"
        else:
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

    if "PH_ATLAS" in data:
        print "pH sensor is present. Trimming all data within PH = ["+str(min_ph)+", "+str(max_ph)+ "] time windows\n"
        PH_data = data["PH_ATLAS"]
        values = PH_data["ph"].values

        ph_outofbounds_indices = np.where( (values < min_ph) | (values > max_ph) )[0] # | out_of_bouds_lat | out_of_bouds_lon )[0]

        if (len(ph_outofbounds_indices) == 0):
            print("no sensor values to prune. all values between "+ str(min_ph) +" and " + str(max_ph))
        else:
            windows = list()
            windows.append([ph_outofbounds_indices[0]])
            left = ph_outofbounds_indices[0]
            for ii in range(1, ph_outofbounds_indices.shape[0]):
                i = ph_outofbounds_indices[ii]
                if i - left > 5:
                    # there has been a jump in index, a new time window has started
                    windows[-1].append(left)
                    windows.append([i])
                left = i
            windows[-1].append(ph_outofbounds_indices[-1])
            # print ph_outofbounds_indices
            # print windows
            for window in windows:
                time_window = [PH_data["ph"].index.values[window[0]], PH_data["ph"].index.values[window[1]]]
                for k in data:
                    data[k] = data[k].loc[np.logical_or(data[k].index < time_window[0], data[k].index > time_window[1])]
    else:
        print "No PH sensor present. No trimming will be performed."

    # Print the available sensors and channels for this logfile.
    print "Available sensors/channels:"
    for s in data.keys():
        if s == 'pose' or s == 'BATTERY':
            continue
        for c in data[s].dtypes.keys():
            print "  {:s}, {:s}".format(s, str(c))
    
    pose = data['pose']
    position = pose[['latitude', 'longitude']]

    out_prefix = log_file + "-"+sensor_name+'-'

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

        csv_output_filename = './csv/'+out_prefix+'csv.csv'
        data_stats["csv_output_filename"] = out_prefix+'csv.csv'
        sensor.to_csv(csv_output_filename)
        
        # Remove columns that have NaN values (no pose information).
        sensor_valid = np.all(np.isfinite(sensor), axis=1)
        sensor = sensor[sensor_valid]

    ## Add a data overlay for the map
    data_bounds = [(position.min() - data_padding).tolist(),
                   (position.max() + data_padding).tolist()]

    # print data
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

    data_stats["number_of_points"] = data_shape[0]
    data_stats["data_bounds"] = data_bounds

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
        # data_stats["data_min"] = data_min
        if (sensor_id == 0):
            # pH
            color_data_min = 6.5
            color_data_max = 9.5
            num_bins = 20
        elif (sensor_id == 1):
            # ec
            num_bins = 20
            color_data_min = 30000
            color_data_max = 95000
        elif (sensor_id == 2):
            # temp
            num_bins = 20
            color_data_min = 5
            color_data_max = 30
        elif (sensor_id == 3):
            # turbidity (DO_ATLAS)
            num_bins = 40
            color_data_min = 0
            color_data_max = 1000

        data_stats["data_stddev"] = data[sensor_name][sensor_channel].std()
        data_stats["data_min"] = data[sensor_name][sensor_channel].min()
        data_stats["data_max"] = data[sensor_name][sensor_channel].max()
        data_stats["data_mean"] = data[sensor_name][sensor_channel].mean()
        histogram_filename = './histograms/'+out_prefix+'histogram.png'
        data_stats["histogram_filename"] = out_prefix+'histogram.png'
        plot_hist_sensor(data, sensor_name, sensor_channel, num_bins, color_data_min, color_data_max, histogram_filename)

        NORMALIZER = color_data_max # 800
        data_zv = (data_zv - color_data_min) / (NORMALIZER - color_data_min)




        print "create color map"
        # Update a color map only at the points that have valid values.
        data_rgb = np.zeros((data_shape[0], data_shape[1], 4), dtype=np.uint8)
        data_rgb = matplotlib.cm.jet(data_zv) * 255
        data_rgb[:,:,3] = 255 * np.isfinite(data_zv)

        # Remove any old image files w/ the same name
        old_png_files = glob.glob('./[overlay,histograms,csv]/'+out_prefix+'-'+sensor_name+'-[overlay,histogram,csv].png')
        for old_png_file in old_png_files:
            print "removing file: " + old_png_file
            os.remove(old_png_file)

        print "creating overlay files"
        png_filename_rgb = './overlay/'+out_prefix+'overlay.png'
        data_stats["overlay_filename"] = out_prefix+'overlay.png'
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
        norm = matplotlib.colors.Normalize(vmin=color_data_min, vmax=NORMALIZER)
        cb1 = matplotlib.colorbar.ColorbarBase(ax1, cmap=cmap,
                                               norm=norm,
                                               orientation='horizontal')
        cb1.set_label(sensor_units)

        scale_bar_filename = './overlay/'+out_prefix+'bar.png'
        data_stats["bar_filename"] = out_prefix+'bar.png'
        pyplot.savefig(scale_bar_filename)

        pyplot.close('all')

        print data_stats
        stats_out = stats_in
        stats_out[str(sensor_id)] = data_stats

        with open("./stats/"+log_file+'.json', 'w') as outfile:
            json.dump(stats_out, outfile, sort_keys=True, indent=4)
    else:
        print "sensor name: " + sensor_name +" is not in:\n", data

def plot_hist_sensor(data, sensor, channel, num_bins, min_value, max_value, filename):
    num_readings = len(data[sensor][channel])

    hist_min = math.floor(min_value)
    hist_max = math.ceil(max_value)
    bin_size = (hist_max - hist_min)/float(num_bins)

    std_dev = data[sensor][channel].std()
    mean = data[sensor][channel].mean()

    bins = np.arange(hist_min, hist_max, bin_size)
    # print bins
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
    plt.ylim(0,100)
    plt.title('Histogram of ' + sensor + " $\mu$="+ "{:.2f}".format(std_dev) +" $\sigma$=" + "{:.2f}".format(mean))
    plt.savefig(filename)
    # plt.text(0, .25, "Standard Dev: " + str(es2_stddev))
    plt.figtext(.16, .75, "Mean: " + str(mean))
    plt.figtext(.16, .7, "std: " + str(std_dev))
    plt.grid(True)
    plt.show()

if __name__ == '__main__':
    if (len(sys.argv) < 3 or (["-h", "help", "h", "--help"] in sys.argv)):
        print "args: python data_processor.py log_file_name (w/o .txt appended) sensor_id min_ec"
        quit(1)
    log_file = sys.argv[1]
    sensor_id = int(sys.argv[2])
    min_ec = int(sys.argv[3])
    max_ec = int(sys.argv[4])
    min_ph = float(sys.argv[5])
    max_ph = float(sys.argv[6])
    min_turbidity = 0
    max_turbidity = 1000
    if (os.path.isfile(log_file)):
        # log_path = sys.argv[1].split("/").join()
        log_file = sys.argv[1].split("/")[-1]
        log_file = log_file.split(".")[-2]
        if ("platypus" not in log_file):
            log_file = sys.argv[1].split(".")[-2]
        if ("platypus" not in log_file):
            print "invalid filename"
            quit(2)
        print log_file
        if sensor_id == -1:
            for x in range(0, 4):
                # try:
                generate_overlay(log_path, log_file, x, [min_ec, max_ec], [min_ph, max_ph], [min_turbidity, max_turbidity])
                # except:
                # print "Failed to generate overlay: " + log_path + ", " + log_file + ", " + str(x)
                print "\n\n\n\n\n\n\n\n\n"
        else:
            # try:
            generate_overlay(log_path, log_file, sensor_id, [min_ec, max_ec], [min_ph, max_ph], [min_turbidity, max_turbidity])
            # except:
            # print "Failed to generate overlay: " + log_path + ", " + log_file + ", " + str(sensor_id)
            print "\n\n\n\n\n\n\n\n\n"
    else:
        log_folder = log_file
        log_files = []
        for file in os.listdir(log_folder):
            if (os.path.isfile(log_folder+"/"+file)):
                print "adding file: " + file
                log_files.append(os.path.splitext(file)[0])
            else:
                print(file +" is not a file")

        print log_files

        for x in log_files:
            if (sensor_id == -1):
                for y in range(0, 4):
                    # try:
                    generate_overlay(log_path, x, y, [min_ec, max_ec], [min_ph, max_ph], [min_turbidity, max_turbidity])
                    # except:
                    # print "Failed to generate overlay: " + log_path + ", " + log_file + ", " + str(y)
                    print "\n\n\n\n\n\n\n\n\n"
            else:
                # try:
                generate_overlay(log_path, x, sensor_id, [min_ec, max_ec], [min_ph, max_ph], [min_turbidity, max_turbidity])
                # except:
                # print "Failed to generate overlay: " + log_path + ", " + log_file + ", " + str(sensor_id)
                print "\n\n\n\n\n\n\n\n\n"

    # generate_histogram()
