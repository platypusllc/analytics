#!/usr/bin/env python
"""
Module containing utility conversion functions.
Copyright 2015. Platypus LLC. All rights reserved.
"""
import utm


def add_ll_to_dataframe(df):
    """
    Converts a UTM position dataframe to also include Lat/Long.

    :param df: a UTM dataframe with a time index and columns
               [easting, northing, altitude, zone, hemi]
    :type  df: pandas.DataFrame
    :returns: the original dataframe with the additional columns
              [longitude, latitude], added in-place
    :rtype:   pandas.DataFrame
    """
    # Create a DataFrame conversion method from UTM to LL coordinates.
    def utm_to_ll(utm_row):
        return utm.to_latlon(utm_row['easting'], utm_row['northing'],
                             utm_row['zone'], northern=utm_row['hemi'])

    # Apply the conversion and add the results to the original dataframe.
    df['latitude'], df['longitude'] = zip(*df.apply(utm_to_ll, axis=1))
    return df
