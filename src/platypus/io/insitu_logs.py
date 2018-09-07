#!/usr/bin/env python
"""
Module for handling the import of various logfiles into numpy arrays.
Copyright 2015. Platypus LLC. All rights reserved.
"""
import collections
import datetime
import logging
import itertools
import pandas

logger = logging.getLogger(__name__)


def merge_files(filename_list):
    """

    :param: filename_list: list of full path filename strings
    :return: One result will all the dataframes merged
    :rtype: {str: pandas.DataFrame}
    """

    logfile_result_list = [load(filename) for filename in filename_list]
    if len(logfile_result_list) == 1:
        return logfile_result_list[0]
    #all_data_types = set()
    #for i in range(1, len(logfile_result_list)):
    #    all_data_types = all_data_types.union(set(logfile_result_list[i].keys()))
    all_data_types = {key for log_dict in logfile_result_list for key in log_dict.keys()}    
    print all_data_types

    merged_dataframe_dict = dict()

    for data_type in all_data_types:
        for i in range(len(logfile_result_list)):
            if data_type in logfile_result_list[i]:
                first_log_index = i
                break
        merged_dataframe_dict[data_type] = logfile_result_list[first_log_index][data_type]
        for i in range(first_log_index + 1, len(logfile_result_list)):
            if data_type in logfile_result_list[i]:
                merged_dataframe_dict[data_type] = merged_dataframe_dict[data_type].combine_first(logfile_result_list[i][data_type]).dropna(how='any')
    return merged_dataframe_dict




def load(filename):
    """
    Loads a log from an in-situ log file (htm or csv)

    Attempts to auto-detect format from the file.

    :param filename: path to a log file
    :type  filename: string
    :returns: a dict containing the data from this logfile
    :rtype: {str: numpy.recarray}
    """
    return pandas.read_csv(filename)
