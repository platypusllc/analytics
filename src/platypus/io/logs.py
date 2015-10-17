#!/usr/bin/env python
"""
Module for handling the import of various logfiles into numpy arrays.
Copyright 2015. Platypus LLC. All rights reserved.
"""
import datetime
import logging
import pandas
import re
from ..util.conversions import add_ll_to_dataframe

logger = logging.getLogger(__name__)

REGEX_FILENAME_V4_0_0 = re.compile(
    r"^airboat"
    r"_(?P<year>\d{4})(?P<month>\d{2})(?P<day>\d{2})"
    r"_(?P<hour>\d{2})(?P<minute>\d{2})(?P<second>\d{2})"
    r".txt$")
"""
Defines a regular expression that represents a filename of the form:
'airboat_YYYYMMDD_HHMMSS.txt', where a date and time are specified. This
format is used in v4.0.0 vehicle logs.
"""

REGEX_LOGRECORD_V4_0_0 = re.compile(
    r"^(?P<timestamp>\d+) "
    r"(?P<hour>\d{2}):(?P<minute>\d{2}):(?P<second>\d{2}),(?P<millis>\d{3}) "
    r"(?P<message>.+\S)\s*$")
"""
Defines a regular expression that represents a log record of the form:
<timestamp> HH:MM:SS,FFF [...], where a date and time are specified. This
format is used in v4.0.0 vehicle log entries.
"""

REGEX_POSE_V4_0_0 = re.compile(
    r"^POSE: \{"
    r"(?P<easting>[\d\.]+), (?P<northing>[\d\.]+), (?P<altitude>[\d\.]+), "
    r"Q\[(?P<roll>[\d\.]+),(?P<pitch>[\d\.]+),(?P<yaw>[\d\.]+)\]"
    r"\} @ (?P<zone>\d+)(?P<hemi>North|South)$")
"""
Defines a regular expression that represents a pose record of the form:
'POSE: {<east>, <north>, <altitude>, Q[<roll>,<pitch>,<yaw>]} @ <zone><hemi>'
This format is used in v4.0.0 vehicle log entries.
"""

REGEX_ES2_V4_0_0 = re.compile(
    r"^ES2: \[e, (?P<ec>[\d\.]+), (?P<temp>[\d\.]+)\]")
"""
Defines a regular expression that represents a pose record of the form:
'ES2: [e, <ec>, <temp>]'
This format is used in v4.0.0 vehicle log entries.
"""


def read_v4_0_0(logfile, start):
    """
    Reads text logs from a Platypus vehicle server logfile.

    :param logfile: the logfile as an iterable
    :type  logfile: python file-like
    :param start: the time at which the log file was started
    :type  start: datetime.datetime
    :returns: a dict containing the data from this logfile
    :rtype: {str: pandas.DataFrame}
    """
    data_pose = []
    data_es2 = []

    for line in logfile:
        # First, parse out the timestamp:
        m = REGEX_LOGRECORD_V4_0_0.match(line)
        if not m:
            logger.warning("Failed to parse log record: {:s}"
                           .format(line))
            continue

        # Construct log record timestamp from start time and offset.
        offset = datetime.timedelta(milliseconds=int(m.group('timestamp')))
        timestamp = start + offset
        message = m.group('message')

        # Check if this is a POSE message.
        m_pose = REGEX_POSE_V4_0_0.match(message)
        if m_pose:
            data_pose.append([timestamp,
                              float(m_pose.group('easting')),
                              float(m_pose.group('northing')),
                              float(m_pose.group('altitude')),
                              int(m_pose.group('zone')),
                              m_pose.group('hemi') == "North"])
            continue

        # Check if this is an ES2 message.
        m_es2 = REGEX_ES2_V4_0_0.match(message)
        if m_es2:
            data_es2.append([timestamp,
                             float(m_es2.group('ec')),
                             float(m_es2.group('temp'))])
            continue

    # Convert the list data to pandas DataFrames and return them.
    return {
        'pose': add_ll_to_dataframe(
                    pandas.DataFrame(data_pose,
                                     columns=('time', 'easting', 'northing',
                                              'altitude', 'zone', 'hemi'))
                          .set_index('time')),
        'es2': pandas.DataFrame(data_es2,
                                columns=('time', 'ec', 'temperature'))
                     .set_index('time')
    }


def load_v4_0_0(filename, *args, **kwargs):
    """
    Loads a log from a v4.1.0 server from a filename.

    :param filename: path to a log file
    :type  filename: string
    :returns: a dict containing the data from this logfile
    :rtype: {str: numpy.recarray}
    """
    # In v4.0.0 files, extract start time from the filename.
    m = REGEX_FILENAME_V4_0_0.match(filename)
    if not m:
        raise ValueError(
            "v4.0.0 log files must be named 'airboat_<date>_<time>.txt'.")
    start = datetime.datetime(int(m.group('year')),
                              int(m.group('month')),
                              int(m.group('day')),
                              int(m.group('hour')),
                              int(m.group('minute')),
                              int(m.group('second')))

    # At the moment, just load this one file.
    with open(filename, 'r') as logfile:
        return read_v4_0_0(logfile, start)


def read(logfile, *args, **kwargs):
    """
    Reads text logs from a Platypus vehicle server logfile.

    Attempts to auto-detect format from the file.

    :param logfile: the logfile as an iterable
    :type  logfile: python file-like
    :returns: a dict containing the data from this logfile
    :rtype: {str: numpy.recarray}
    """
    # TODO: support multiple log types
    return read_v4_0_0(logfile, *args, **kwargs)


def load(filename, *args, **kwargs):
    """
    Loads a log from a Platypus vehicle server from a filename.

    Attempts to auto-detect format from the file.

    :param filename: path to a log file
    :type  filename: string
    :returns: a dict containing the data from this logfile
    :rtype: {str: numpy.recarray}
    """
    # TODO: support multiple log types
    return load_v4_0_0(filename, *args, **kwargs)
