#!/usr/bin/env python
"""
Module for handling the import of various logfiles into numpy arrays.
Copyright 2015. Platypus LLC. All rights reserved.
"""
import numpy as np


def read_v4_0_0(logfile):
    """
    Reads text logs from a Platypus vehicle server logfile.

    :param logfile: the logfile as an iterable
    :type  logfile: python file-like
    :returns: a struct containing the data from this logfile.
    :rtype: numpy.recarray
    """
    for line in logfile:
        print logfile


def load_v4_0_0(filename, *args, **kwargs):
    """
    Loads a log from a v4.1.0 server from a filename.

    :param filename: path to a log file
    :type  filename: string
    :returns: a struct containing the data from this logfile.
    :rtype: numpy.recarray
    """
    # At the moment, just load this one file.
    with open(filename, 'r') as logfile:
        return read_v4_0_0(logfile)


def read(logfile, *args, **kwargs):
    """
    Reads text logs from a Platypus vehicle server logfile.

    Attempts to auto-detect format from the file.

    :param logfile: the logfile as an iterable
    :type  logfile: python file-like
    :returns: a struct containing the data from this logfile.
    :rtype: numpy.recarray
    """
    # TODO: support multiple log types
    return read_v4_0_0(logfile, *args, **kwargs)


def load(filename, *args, **kwargs):
    """
    Loads a log from a Platypus vehicle server from a filename.

    Attempts to auto-detect format from the file.

    :param filename: path to a log file
    :type  filename: string
    :returns: a struct containing the data from this logfile.
    :rtype: numpy.recarray
    """
    # TODO: support multiple log types
    return load_v4_0_0(filename, *args, **kwargs)
