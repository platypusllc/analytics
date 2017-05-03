import matplotlib.pyplot as plt
import platypus.io.logs
import platypus.util.conversions
import numpy as np

PATH = "/home/jason/Documents/INTCATCH/phone logs/lorenzo dataset/"
FILE = "platypus_20170420_050906.txt"


def main():
    global PATH, FILE
    print "\nLoading all the data in " + PATH + FILE + "\n"
    data = platypus.io.logs.load(PATH + FILE)
    if "ES2" in data:
        print "ES2 sensor is present. Trimming all data within EC = 0 time windows\n"
        # find all time windows where EC is exactly 0
        ES2_data = data["ES2"]
        values = ES2_data["ec"].values
        ec_eq_zero_indices = np.where(values == 0)[0]
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


if __name__ == "__main__":
    main()
