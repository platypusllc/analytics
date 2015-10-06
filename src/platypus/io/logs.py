#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Module for handling the import of various logfiles into numpy arrays.
Copyright 2015. Platypus LLC. All rights reserved.
"""


def read_v4_0_0(logfile):
    """
    Reads text logs from v4.1.0 server.

    :param logfile: the logfile as an iterable
    :type  logfile: python file-like
    :returns: a numpy recarray containing the data from this logfile.
    """
    for line in logfile:
        # TODO: fill me in!
        pass


def load_v4_0_0(filename, *args, **kwargs):
    """
    Loads a log from a v4.1.0 server from a filename.

    :param filename: path to a log file
    :type  filename: string
    :returns: a numpy recarray containing the data from this logfile.
    """
    # At the moment, just load this one file.
    with open(filename, 'r') as logfile:
        return read_v4_0_0(logfile)
