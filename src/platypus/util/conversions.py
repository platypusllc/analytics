"""
Module containing utility conversion functions.
Copyright 2015. Platypus LLC. All rights reserved.
"""
import utm


def add_ll_to_pose_dataframe(df):
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


def region_from_points(df):
    """
    Computes a convex-hull region boundary from the provided 'pose' dataframe.

    :param df: A dataframe containing `longitude` and `latitude` as columns
    :type  df: pandas.DataFrame
    :returns: convex hull of positions in `pose`
    :rtype: GeoJSON polyline defining region boundary
    """
    raise NotImplementedError()


def remove_outliers_from_pose_dataframe(df, tolerance=10000):
    """
    Remove poses more than a certain number of meters from the median pose.

    These poses are usually due to GPS initialization error, and typically
    should be excluded from interpolations.  The default tolerance is 10km.

    :param df: a UTM dataframe with time index and [easting, northing] columns
    :type  df: pandas.DataFrame
    :param tolerance: maximum distance in meters from median of dataset
    :type  tolerance: float
    :returns: A dataframe with rows exceeding the specified tolerance removed
    :rtype: pandas.DataFrame
    """
    median_easting = df['easting'].median()
    median_northing = df['northing'].median()

    valid_easting = abs(df['easting'] - median_easting) < tolerance
    valid_northing = abs(df['northing'] - median_northing) < tolerance

    return df[valid_northing & valid_easting]
