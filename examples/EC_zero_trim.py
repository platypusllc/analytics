import collections
import platypus.io.logs
import platypus.util.conversions
import numpy as np
import datetime
import json
import six
import re
import pandas

PATH = "/home/jason/Documents/INTCATCH/phone logs/Gardaland outlet/2017-10-3/"
FILE = "platypus_20171003_050016"
EXT = ".txt"


"""
def trim_EC():
    global PATH, FILE
    print "\nLoading all the data in " + PATH + FILE + "\n"
    data = platypus.io.logs.load(PATH + FILE)
    if "ES2" in data:
        print "ES2 sensor is present. Trimming all data within EC < 100 time windows\n"
        # find all time windows where EC is exactly 0
        ES2_data = data["ES2"]
        values = ES2_data["ec"].values
        ec_eq_zero_indices = np.where(values < 100)[0]
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
            for k in data.keys():
                data[k] = data[k].loc[np.logical_or(data[k].index < time_window[0], data[k].index > time_window[1])]

    else:
        print "No ES2 sensor present. No trimming will be performed."

    # do stuff with data
"""


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


def data_with_sampler():
    global PATH, FILE
    filename = PATH + FILE + EXT
    data = platypus.io.logs.load(filename)
    is_EC_gt_100 = False

    jar_start_timestamps = dict()
    with open(filename, 'r') as logfile:
        raw_data = collections.defaultdict(list)
        start_time = datetime.datetime.utcfromtimestamp(0)

        for line in logfile:
            # Extract each line fron the logfile and convert the timestamp.
            time_offset_ms, level, message = line.split('\t', 2)

            # Compute the timestamp for each log entry.
            time_offset = datetime.timedelta(milliseconds=int(time_offset_ms))
            timestamp = start_time + time_offset

            # Try to parse the log as a JSON object.
            try:
                entry = json.loads(message)
            except ValueError as e:
                raise ValueError(
                    "Aborted after invalid JSON log message '{:s}': {:s}".format(message, e))

            # If the line is a datetime, compute subsequent timestamps from this.
            # We assume that "date" and "time" are always together in the entry.
            if 'date' in entry:
                timestamp = datetime.datetime.utcfromtimestamp(entry['time'] / 1000.)
                start_time = timestamp - time_offset

            # Extract appropriate data from each entry.
            for k, v in six.viewitems(entry):
                if k == 'sensor':
                    if v['type'] == "ES2":
                        ec = v['data'][0]
                        if not is_EC_gt_100 and ec > 100:
                            is_EC_gt_100 = True
                        if is_EC_gt_100 and ec < 100:
                            is_EC_gt_100 = False
                if k == 'sampler' and is_EC_gt_100:
                    if "start" in v:
                        # the in-water sampler start messages
                        m = re.search('[0-9]+', v)
                        jar_id = m.group(0)
                        jar_start_timestamps[jar_id] = timestamp

                        # TODO: MUST MERGE IN THE LATITUDE AND LONGITUDE!!!

    return data, jar_start_timestamps


if __name__ == "__main__":
    global PATH, FILE
    filename = PATH + FILE + EXT

    data, jar_start_timestamps = data_with_sampler()
    trimmed_data = trim_using_EC(data)
    for k in jar_start_timestamps:
        start_time = jar_start_timestamps[k]
        end_time = start_time + datetime.timedelta(minutes=3.75)
        print "Jar {} lasts from {} to {}".format(k, start_time, end_time)
        for sensor in data.keys():
            print sensor
            if sensor not in ["ES2", "ATLAS_DO", "ATLAS_PH"]:
                continue
            dataframe = trimmed_data[sensor]
            relevantframe = dataframe.between_time(start_time.time(), end_time.time())
            output_filename = PATH + FILE + "__JAR_{}".format(k) + "__{}".format(sensor) + ".csv"
            relevantframe.to_csv(output_filename)


