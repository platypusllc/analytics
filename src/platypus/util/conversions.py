#!/usr/bin/env python
"""
Module containing utility conversion functions.
Copyright 2015. Platypus LLC. All rights reserved.
"""
import utm
import numpy as np
import numpy.lib.recfunctions


def add_ll_to_pose_dataframe(df):
    """
    Converts a UTM position dataframe to also include Lat/Long.

    :param df: a UTM array with columns
               [time, easting, northing, altitude, zone, hemi]
    :type  df: numpy.array
    :returns: the original array with the additional columns
              [longitude, latitude], added in-place
    :rtype:   numpy.array
    """
    # Create a vectorized conversion method from UTM to LL coordinates.
    def _utm_to_ll(row):
        easting, northing, zone, hemi = row
        return utm.to_latlon(easting, northing, zone, northern=hemi)
    utm_to_ll = np.vectorize(_utm_to_ll)
    ll = utm_to_ll(df[['easting', 'northing', 'zone', 'hemi']])

    # Apply the conversion and add the results to the original dataframe.
    return numpy.lib.recfunctions.rec_append_fields(
        df, ('latitude', 'longitude'), ll)


def region_from_points(df):
    """
    Computes a convex-hull region boundary from the provided 'pose' dataframe.

    :param df: A dataframe containing `longitude` and `latitude` as columns
    :type  df: numpy.array
    :returns: convex hull of positions in `pose`
    :rtype: GeoJSON polyline defining region boundary
    """
    raise NotImplementedError()


def remove_outliers_from_pose_dataframe(df, tolerance=10000):
    """
    Remove poses more than a certain number of meters from the median pose.

    These poses are usually due to GPS initialization error, and typically
    should be excluded from interpolations.  The default tolerance is 10km.

    :param df: a UTM dataframe with [time, easting, northing] columns
    :type  df: numpy.array
    :param tolerance: maximum distance in meters from median of dataset
    :type  tolerance: float
    :returns: An array with rows exceeding the specified tolerance removed
    :rtype: numpy.array
    """
    median_easting = np.median(df['easting'])
    median_northing = np.median(df['northing'])

    valid_easting = abs(df['easting'] - median_easting) < tolerance
    valid_northing = abs(df['northing'] - median_northing) < tolerance

    return df[valid_northing & valid_easting]
