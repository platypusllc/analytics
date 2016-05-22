#!/usr/bin/env python
"""
Module for handling the import of various logfiles into numpy arrays.
Copyright 2015. Platypus LLC. All rights reserved.
"""
import collections
import datetime
import logging
import itertools
import json
import numpy as np
import re
import six
from ..util.conversions import (
    add_ll_to_pose_dataframe,
    remove_outliers_from_pose_dataframe,
)

logger = logging.getLogger(__name__)

_REGEX_FLOAT = r"[-+]?[0-9]*\.?[0-9]+"
"""
Defines the regex string for a floating point decimal number.
"""

_REGEX_FILENAME_V4_0_0 = re.compile(
    r".*airboat"
    r"_(?P<year>\d{4})(?P<month>\d{2})(?P<day>\d{2})"
    r"_(?P<hour>\d{2})(?P<minute>\d{2})(?P<second>\d{2})"
    r".txt$")
"""
Defines a regular expression that represents a filename of the form:
'airboat_YYYYMMDD_HHMMSS.txt', where a date and time are specified. This
format is used in v4.0.0 vehicle logs.
"""

_REGEX_LOGRECORD_V4_0_0 = re.compile(
    r"^(?P<timestamp>\d+) "
    r"(?P<hour>\d{2}):(?P<minute>\d{2}):(?P<second>\d{2}),(?P<millis>\d+) "
    r"(?P<message>.+\S)\s*$")
"""
Defines a regular expression that represents a log record of the form:
<timestamp> HH:MM:SS,FFF [...], where a date and time are specified. This
format is used in v4.0.0 vehicle log entries.
"""

_REGEX_POSE_V4_0_0 = re.compile(
    r"^POSE: \{{"
    r"(?P<easting>{number}), (?P<northing>{number}), (?P<altitude>{number}), "
    r"Q\[(?P<roll>{number}),(?P<pitch>{number}),(?P<yaw>{number})\]"
    r"\}} @ (?P<zone>\d+)(?P<hemi>North|South)$"
    .format(number=_REGEX_FLOAT))
"""
Defines a regular expression that represents a pose record of the form:
'POSE: {<east>, <north>, <altitude>, Q[<roll>,<pitch>,<yaw>]} @ <zone><hemi>'
This format is used in v4.0.0 vehicle log entries.
"""

_REGEX_ES2_V4_0_0 = re.compile(
    r"^ES2: \[e, (?P<ec>[\d\.]+), (?P<temp>[\d\.]+)\]")
"""
Defines a regular expression that represents a pose record of the form:
'ES2: [e, <ec>, <temp>]'
This format is used in v4.0.0 vehicle log entries.
"""


_REGEX_SENSOR_V4_0_0 = re.compile(
    r"^SENSOR(?P<index>\d+): "
    r"\{\"data\":\"(?P<data>.+)\",\"type\":\"(?P<type>\S+)\"\}")
"""
Defines a regular expression that represents generic sensor record of the form:
'SENSOR1: {"data":"7.78","type":"atlas_do"}'
This format is used in v4.2.0 vehicle log entries.
"""

_DATA_FIELDS_v4_0_0 = {
    'battery': ('voltage', 'm0_current', 'm1_current'),
    'es2': ('ec', 'temperature'),
    'atlas_do': ('do',),
    'atlas_ph': ('ph',),
}
"""
Defines dataframe field names for known data types in v4.0.0 logfiles.
"""

_DATA_FIELDS_v4_1_0 = {
    'BATTERY': ('voltage', 'm0_current', 'm1_current'),
    'ES2': ('ec', 'temperature'),
    'ATLAS_DO': ('do',),
    'ATLAS_PH': ('ph',),
}
"""
Defines dataframe field names for known data types in v4.1.0 logfiles.
"""

_DATA_FIELDS_v4_2_0 = {
    'BATTERY': ('voltage', 'm0_current', 'm1_current'),
    'ES2': ('ec', 'temperature'),
    'ATLAS_DO': ('do',),
    'ATLAS_PH': ('ph',),
}
"""
Defines dataframe field names for known data types in v4.2.0 logfiles.
"""


def read_v4_2_0(logfile):
    """
    Reads text logs from a Platypus vehicle server logfile.

    :param logfile: the logfile as an iterable
    :type  logfile: python file-like
    :returns: a dict containing the data from this logfile
    :rtype: {str: numpy.rec.array}
    """
    raw_data = collections.defaultdict(list)
    start_time = np.datetime64(0, 'ms')

    for line in logfile:
        # Extract each line fron the logfile and convert the timestamp.
        time_offset_ms, level, message = line.split('\t', 2)

        # Compute the timestamp for each log entry.
        time_offset = np.timedelta64(int(time_offset_ms), 'ms')
        timestamp = np.datetime64(start_time + time_offset)

        # Try to parse the log as a JSON object.
        try:
            entry = json.loads(message)
        except ValueError as e:
            raise ValueError(
                "Aborted after invalid JSON log message '{:s}': {:s}"
                .format(message, e))

        # If the line is a datetime, compute subsequent timestamps from this.
        # We assume that "date" and "time" are always together in the entry.
        if 'date' in entry:
            timestamp = np.datetime64(entry['time'], 'ms')
            start_time = timestamp - time_offset

        # Extract appropriate data from each entry.
        for k, v in six.viewitems(entry):
            if k == 'pose':
                zone = int(v['zone'][:-5])
                hemi = v['zone'].endswith('North')
                raw_data[k].append([
                    timestamp,
                    v['p'][0],
                    v['p'][1],
                    v['p'][2],
                    zone, hemi
                ])
            elif k == 'sensor':
                raw_data[v['type']].append(
                    [timestamp] + v['data']
                )
            else:
                pass

    # Convert the list data to numpy recarrays and return them.
    # For known types, clean up and label the data.
    data = {}

    for k, v in six.viewitems(raw_data):
        if k == 'pose':
            data['pose'] = add_ll_to_pose_dataframe(
                remove_outliers_from_pose_dataframe(
                    np.rec.array(v, dtype=[('time', 'datetime64[ms]'),
                                           ('easting', float),
                                           ('northing', float),
                                           ('altitude', float),
                                           ('zone', int),
                                           ('hemi', bool)])
                )
            )
        elif k in _DATA_FIELDS_v4_2_0:
            fields = [('time', 'datetime64[ms]')]
            fields += [(field_name, float)
                       for field_name in _DATA_FIELDS_v4_2_0[k]]
            data[k] = np.rec.array(v, dtype=fields)

    return data


def read_v4_1_0(logfile):
    """
    Reads text logs from a Platypus vehicle server logfile.

    :param logfile: the logfile as an iterable
    :type  logfile: python file-like
    :returns: a dict containing the data from this logfile
    :rtype: {str: numpy.rec.array}
    """
    raw_data = collections.defaultdict(list)
    start_time = np.datetime64(0, 'ms')

    for line in logfile:
        # Extract each line fron the logfile and convert the timestamp.
        time_offset_ms, date, message = line.split(' ', 2)

        # Compute the timestamp for each log entry.
        time_offset = np.timedelta64(int(time_offset_ms), 'ms')
        timestamp = start_time + time_offset

        # Try to parse the log as a JSON object.
        try:
            entry = json.loads(message)
        except ValueError as e:
            raise ValueError(
                "Aborted after invalid JSON log message '{:s}': {:s}"
                .format(message, e))

        # Extract appropriate data from each entry.
        for k, v in six.viewitems(entry):
            if k == 'pose':
                zone = int(v['zone'][:-5])
                hemi = v['zone'].endswith('North')
                raw_data[k].append([
                    timestamp,
                    v['p'][0],
                    v['p'][1],
                    v['p'][2],
                    zone, hemi
                ])
            elif k == 'sensor':
                raw_data[v['type']].append(
                    [timestamp] + v['data']
                )
            else:
                pass

    # Convert the list data to numpy recarrays and return them.
    # For known types, clean up and label the data.
    data = {}

    for k, v in six.viewitems(raw_data):
        if k == 'pose':
            data['pose'] = add_ll_to_pose_dataframe(
                remove_outliers_from_pose_dataframe(
                    np.rec.array(v, dtype=[('time', 'datetime64[ms]'),
                                           ('easting', float),
                                           ('northing', float),
                                           ('altitude', float),
                                           ('zone', int),
                                           ('hemi', bool)])
                )
            )
        elif k in _DATA_FIELDS_v4_1_0:
            fields = [('time', 'datetime64[ms]')]
            fields += [(field_name, float)
                       for field_name in _DATA_FIELDS_v4_2_0[k]]
            data[k] = np.rec.array(v, dtype=fields)

    return data


def read_v4_0_0(logfile, filename):
    """
    Reads text logs from a Platypus vehicle server logfile.

    :param logfile: the logfile as an iterable
    :type  logfile: python file-like
    :param filename: the name of the logfile containing the start time.
    :type  filename: str
    :returns: a dict containing the data from this logfile
    :rtype: {str: numpy.recarray}
    """
    data_pose = []
    data_sensors = {}

    # In v4.0.0 files, extract start time from the filename.
    m = _REGEX_FILENAME_V4_0_0.match(filename)
    if not m:
        raise ValueError(
            "v4.0.0 log files must be named 'airboat_<date>_<time>.txt'.")
    start_time = np.datetime64(datetime.datetime(
        int(m.group('year')),
        int(m.group('month')),
        int(m.group('day')),
        int(m.group('hour')),
        int(m.group('minute')),
        int(m.group('second'))
    ))

    for line in logfile:
        # First, parse out the timestamp:
        m = _REGEX_LOGRECORD_V4_0_0.match(line)
        if not m:
            logger.warning("Failed to parse log record: {:s}"
                           .format(line))
            continue

        # Construct log record timestamp from start time and offset.
        time_offset = np.timedelta64(int(m.group('timestamp')), 'ms')
        timestamp = start_time + time_offset
        message = m.group('message')

        # Check if this is a POSE message.
        m_pose = _REGEX_POSE_V4_0_0.match(message)
        if m_pose:
            data_pose.append([timestamp,
                              float(m_pose.group('easting')),
                              float(m_pose.group('northing')),
                              float(m_pose.group('altitude')),
                              int(m_pose.group('zone')),
                              m_pose.group('hemi') == "North"])
            continue

        # Check if this is an ES2 message.
        m_es2 = _REGEX_ES2_V4_0_0.match(message)
        if m_es2:
            if 'es2' not in data_sensors:
                data_sensors['es2'] = []
            data_sensors['es2'].append([timestamp,
                                        float(m_es2.group('ec')),
                                        float(m_es2.group('temp'))])
            continue

        m_sensor = _REGEX_SENSOR_V4_0_0.match(message)
        if m_sensor:
            # Extract the sensor type and the data.
            type_sensor = m_sensor.group('type')
            data_sensor = [float(datum)
                           for datum in m_sensor.group('data').split(" ")]

            # Add the sensor if it does not already exist in the data map.
            if type_sensor not in data_sensors:
                data_sensors[type_sensor] = []

            # Insert the new sensor reading into the appropriate list.
            data_sensor.insert(0, timestamp)
            data_sensors[m_sensor.group('type')].append(data_sensor)
            continue

    # Convert the list data to numpy recarrays and return them.
    # For known types, clean up and label the data.
    data = {}

    data['pose'] = add_ll_to_pose_dataframe(
            remove_outliers_from_pose_dataframe(
                np.rec.array(data_pose, dtype=[('time', 'datetime64[ms]'),
                                               ('easting', float),
                                               ('northing', float),
                                               ('altitude', float),
                                               ('zone', int),
                                               ('hemi', bool)])
            )
        )

    for k, v in six.viewitems(data_sensors):
        if k in _DATA_FIELDS_v4_0_0:
            fields = [('time', 'datetime64[ms]')]
            fields += [(field_name, float)
                       for field_name in _DATA_FIELDS_v4_0_0[k]]
            data[k] = np.rec.array(v, dtype=fields)

    # Return merged data structure.
    return data


def load_v4_2_0(filename, *args, **kwargs):
    """
    Loads a log from a v4.2.0 server from a filename.

    :param filename: path to a log file
    :type  filename: string
    :returns: a dict containing the data from this logfile
    :rtype: {str: numpy.recarray}
    """
    with open(filename, 'r') as logfile:
        return read_v4_2_0(logfile)


def load_v4_1_0(filename, *args, **kwargs):
    """
    Loads a log from a v4.1.0 server from a filename.

    :param filename: path to a log file
    :type  filename: string
    :returns: a dict containing the data from this logfile
    :rtype: {str: numpy.recarray}
    """
    with open(filename, 'r') as logfile:
        return read_v4_1_0(logfile)


def load_v4_0_0(filename, *args, **kwargs):
    """
    Loads a log from a v4.0.0 server from a filename.

    :param filename: path to a log file
    :type  filename: string
    :returns: a dict containing the data from this logfile
    :rtype: {str: numpy.recarray}
    """
    with open(filename, 'r') as logfile:
        return read_v4_0_0(logfile, filename)


def read(logfile, filename=None):
    """
    Reads text logs from a Platypus vehicle server logfile.

    Attempts to auto-detect format from the file.

    :param logfile: the logfile as an iterable
    :type  logfile: python file-like
    :param filename: (optional) name of file that was loaded
    :type  filename: str
    :returns: a dict containing the data from this logfile
    :rtype: {str: numpy.recarray}
    """
    # Peek at the first line of the file.
    peek, logfile = itertools.tee(logfile)
    line = next(peek)
    components = re.split("[ \t]", line, 2)

    # Depending on the format of the first line, pick an appropriate loader.
    if len(components[1]) == 1:
        # Version 4.2.0 files have a single-character log-level.
        return read_v4_2_0(logfile)
    else:
        try:
            # Version 4.1.0 logs have JSON messages.
            json.loads(components[2])
            return read_v4_1_0(logfile)
        except ValueError:
            # If all else fails, use the version 4.0.0 parser.
            return read_v4_0_0(logfile, filename=filename)


def load(filename):
    """
    Loads a log from a Platypus vehicle server from a filename.

    Attempts to auto-detect format from the file.

    :param filename: path to a log file
    :type  filename: string
    :returns: a dict containing the data from this logfile
    :rtype: {str: numpy.recarray}
    """
    with open(filename, 'r') as logfile:
        return read(logfile, filename=filename)
