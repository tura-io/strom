"""Class for creating derived parameters from measures
This is a subclass of the Transformer class that creates derived measures from input measures.
The process of deriving measures takes input measures and uses them to calculate a new measure
such as finding distance from a positional measure or the slope of an input measure. Derived
measures may be of difference dimension than their inputs.
These DeriveParam functions are called by apply_transformer on BStream data and the results are
stored as BStream["derived_measures"]
"""

import numpy as np
import pandas as pd

from strom.utils.logger.logger import logger
from .filter_data import window_data


def sloper(rise_array, run_array, window_len=1):
    """
    Function to calculate slope of two rates of change using the classic rise over run formula
    :param rise_array: data for numerator of rise/run
    :type rise_array: numpy array
    :param run_array: data for denominator of rise/run
    :type run_array: numpy array
    :param window_len: length of window for averaging slope
    :type window_len: int
    :return: rise_array/run_array
    :rtype: numpy array
    """
    sloped = rise_array / run_array
    if window_len > 1:
        sloped = window_data(sloped, window_len)

    return sloped


def DeriveSlope(data_frame, params=None):
    logger.debug("Starting DeriveSlope.")

    if params==None:
        params = {}
        params["func_params"] = {"window_len":("length of averaging window",1,False)}
        params["measure_rules"] ={
                                    "rise_measure":("measure y values (or rise in rise/run calculation of slope)","measure_name",True),
                                    "run_measure":("measure containing x values (or run in rise/run calculation of slope)","measure_name",True),
                                    "output_name":("name of returned measure","output_name",True)
                                    }
        return params

    logger.debug("transforming data to %s" % (params["measure_rules"]["output_name"]))
    if "window_len" in params["func_params"]:
        window_len = params["func_params"]["window_len"]
    else:
        window_len = 1
    xrun = data_frame[params["measure_rules"]["run_measure"]].values
    yrise = data_frame[params["measure_rules"]["rise_measure"]].values
    smaller_len = np.min([xrun.shape[0], yrise.shape[0]])
    sloped = sloper(yrise[:smaller_len,], xrun[:smaller_len,], window_len)
    return pd.DataFrame(data=sloped, columns=[params["measure_rules"]["output_name"]], index=data_frame.index)


def diff_data(data_array, window_len=1, angle_diff=False):
    """
    Function to calculate the difference between samples in an array
    :param data_array: input data
    :type data_array: numpy array
    :param window_len: window length for smoothing
    :type window_len: int
    :param angle_diff: Specify if the angular difference between samples should be calculated instead of raw diff
    :type angle_diff: Boolean
    :return: diff between samples in data_array
    :rtype: numpy array
    """
    logger.debug("diffing data")
    diffed_data = np.diff(data_array)
    if angle_diff:
        diffed_data = (diffed_data + 180.0) % 360 - 180
    if window_len > 1:
        diffed_data = window_data(diffed_data, window_len)
    return diffed_data

def DeriveChange(data_frame, params=None):
    logger.debug("initialized DeriveChange. Use get_params() to see parameter values")
    if params==None:
        params = {}
        params["func_params"] = {"window_len":("length of averaging window",1,False), "angle_change":("if the change is between angles, we return the signed smaller angle between the two headings",False, False)}
        params["measure_rules"] ={
                                    "target_measure":("name of the target measure","measure_name",True),
                                    "output_name":("name of returned measure","output_name",True)
                                    }
        return params

    logger.debug("transforming data to %s" % (params["measure_rules"]["output_name"]))
    if "window_len" in params["func_params"]:
        window_len = params["func_params"]["window_len"]
    else:
        window_len = 1
    target_array = data_frame[params["measure_rules"]["target_measure"]].values
    diffed_data = diff_data(target_array, window_len, params["func_params"]["angle_change"])
    return pd.DataFrame(data=diffed_data, columns=[params["measure_rules"]["output_name"]], index=data_frame.index[:-1])


def cumsum(data_array, offset=0):
    """
    Calculate the cumulative sum of a vector
    :param data_array: data to be summed
    :type data_array: numpy array
    :param offset: starting value for sum
    :type offset: float
    :return: the cumulative sum of the data_array
    :rtype: numpy array
    """
    logger.debug("cumsum")
    return np.cumsum(data_array)+offset


def DeriveCumsum(data_frame, params=None):
    logger.debug("initialized DeriveCumsum. Use get_params() to see parameter values")
    if params == None:
        params = {}
        params["func_params"] = {"offset":("initial offset value for starting sum",0,False)}
        params["measure_rules"] = {
                                    "target_measure":("name of the target measure","measure_name",True),
                                    "output_name":("name of returned measure","output_name",True)
                                    }
        return params

    logger.debug("transforming data to %s" % (params["measure_rules"]["output_name"]))
    target_array = data_frame[params["measure_rules"]["target_measure"]].values
    cumsum_array = cumsum(target_array, params["func_params"]["offset"])
    return pd.DataFrame(data=cumsum_array, columns=[params["measure_rules"]["output_name"]], index=data_frame.index)


def euclidean_dist(position_array, window_len=1):
    """
    Function to calculate euclidean distance between consecutive samples in a positional vector
    :param position_array: input vector of positions
    :type position_array: N x 2 numpy array
    :param window_len: length of window for averaging output
    :type window_len: int
    :return: distances between consecutive points
    :rtype: (N-1) x 1 numpy array
    """
    logger.debug("calculating euclidean distance")
    euclid_array = np.sqrt(np.sum(np.diff(position_array, axis=0)**2, axis=1))
    if window_len > 1:
        euclid_array = window_data(euclid_array, window_len)
    return  euclid_array

def great_circle(position_array, window_len=1, units="mi"):
    """
    Function to calculate the great circle distance between consecutive samples in lat lon vector
    :param position_array: input vector of lat lon points
    :type position_array: N x 2 numpy array
    :param window_len: length of window for averaging output
    :type window_len: int
    :param units: String for output units. Currently 'mi' and 'km' supported
    :type units: str
    :return: distances between consecutive points
    :rtype: (N-1) x 1 numpy array

    """
    logger.debug("calculating great circle distance")
    lat1 = position_array[:-1, 0]
    lat2 = position_array[1:, 0]
    lon1 = position_array[:-1, 1]
    lon2 = position_array[1:, 1]
    lon1, lat1, lon2, lat2 = map(np.radians, [lon1, lat1, lon2, lat2])
    dlat = lat1 - lat2
    dlon = lon1 - lon2
    inner_val = np.sin(dlat/2.0)**2 + np.cos(lat1) * np.cos(lat2) * np.sin(dlon/2.0)**2
    outer_val = 2*np.arcsin(np.sqrt(inner_val))
    if units == "mi":
        earth_diameter = 3959
    elif units == "km":
        earth_diameter = 6371

    great_dist = outer_val*earth_diameter
    if window_len > 1:
        great_dist = window_data(great_dist, window_len)
    return great_dist


def DeriveDistance(data_frame, params=None):
    logger.debug("initialized DeriveDistance. Use get_params() to see parameter values")
    if params == None:
        params = {}
        params["func_params"] = {
                                    "window_len":("length of averaging window",1,False),
                                    "distance_func": ("distance function to use, \"euclidea\" and \"great_circle\" supported", "euclidean",True),
                                    "swap_lon_lat":("Are columns in data lon before lat? if so, set to True",False,True)
                                 }
        params["supported_distances"] = ("List of supported distance metrics",["euclidean", "great_circle"],False)
        params["measure_rules"] = {
                                    "spatial_measure":("name of geo-spatial measure","measure_name",True),
                                    "output_name":("name of returned measure","measure_name",True)
                                    }
        return params


    logger.debug("transforming data to %s" % (params["measure_rules"]["output_name"]))
    if "window_len" in params["func_params"]:
        window_len = params["func_params"]["window_len"]
    else:
        window_len = 1
    position_array = pd.DataFrame(data_frame[params["measure_rules"]["spatial_measure"]].tolist()).values

    if params["func_params"]["swap_lon_lat"]:
        position_array = position_array[:,[1, 0]]
    if params["func_params"]["distance_func"] == "euclidean":
        dist_array = euclidean_dist(position_array, window_len)
    elif params["func_params"]["distance_func"] == "great_circle":
        dist_array = great_circle(position_array, window_len)
    else:
        raise ValueError("Not suported distance function")

    return pd.DataFrame(data=dist_array, columns=[params["measure_rules"]["output_name"]], index=data_frame.index[:-1])


def flat_angle(position_array, window_len, units="deg"):
    """
    Function for computing the angle between samples from a 2D plane
    :param position_array:input vector of positions
    :type position_array: N x 2 numpy array
    :param window_len: length of window for smoothing
    :type window_len: int
    :param units: deg or rad for degrees or radians
    :type units: str
    :return: the angle between consecutive samples
    :rtype: (N-1) x 1 numpy array
    """
    logger.debug("finding cartesian angle of vector")
    diff_array = np.diff(position_array, axis=0)
    diff_angle = np.arctan2(diff_array[:,1], diff_array[:,0])
    if units == "deg":
        diff_angle = (np.rad2deg(diff_angle) + 180.0 ) % 360 - 180
    elif units == "rad":
        diff_angle = (diff_angle + 2*np.pi) % np.pi
    if window_len > 1:
        diff_angle = window_data(diff_angle, window_len)
    return diff_angle

def bearing(position_array, window_len, units="deg"):
    """
    Calculates the angle between lat lon points
    :param position_array: input vector of lat lon points
    :type position_array: N x 2 numpy array
    :param window_len: Length of window for averaging
    :type window_len: int
    :param units: String for output units. Currently 'mi' and 'km' supported
    :type units: str
    :return: the angle between consecutive latlon points
    :rtype: (N - 1) x 1 numpy array
    """
    logger.debug("finding bearing of vector")
    lat1 = position_array[:-1, 0]
    lat2 = position_array[1:, 0]
    lon1 = position_array[:-1, 1]
    lon2 = position_array[1:, 1]
    lon1, lat1, lon2, lat2 = map(np.radians, [lon1, lat1, lon2, lat2])
    dlon = lon1 - lon2
    first_val = np.sin(dlon)*np.cos(lat2)
    second_val = np.cos(lat1)*np.sin(lat2)-np.sin(lat1)*np.cos(lat2)*np.cos(dlon)
    cur_bear = np.arctan2(first_val, second_val)
    if units == "deg":
        cur_bear = (np.rad2deg(cur_bear) + 180.0 ) % 360 - 180
    if window_len > 1:
        cur_bear = window_data(cur_bear, window_len)
    return cur_bear


def DeriveHeading(data_frame, params=None):
    logger.debug("initialized DeriveHeading. Use get_params() to see parameter values")
    if params == None:
        params = {}
        params["func_params"] = {
                                "window_len": ("length of averaging window", 1, False),
                                "units":("units for heading","deg",True),
                                "heading_type":("type of heading to compute","bearing",True),
                                "swap_lon_lat": ("Are columns in data lon before lat? if so, set to True", False, True)
        }
        params["measure_rules"] = {
                                    "spatial_measure":("name of geo-spatial measure","measure_name",True),
                                    "output_name":("name of returned measure","measure_name",True)
                                    }
        return params


    logger.debug("transforming data to %s" % (params["measure_rules"]["output_name"]))
    if "window_len" in params["func_params"]:
        window_len = params["func_params"]["window_len"]
    else:
        window_len = 1
    position_array = pd.DataFrame(data_frame[params["measure_rules"]["spatial_measure"]].tolist()).values

    if params["func_params"]["swap_lon_lat"]:
        position_array = position_array[:,[1, 0]]
    if params["func_params"]["heading_type"] == "bearing":
        angle_array = bearing(position_array, window_len, params["func_params"]["units"])
    elif params["func_params"]["heading_type"] == "flat_angle":
        angle_array = flat_angle(position_array, window_len, params["func_params"]["units"])

    return pd.DataFrame(data=angle_array, columns=[params["measure_rules"]["output_name"]], index=data_frame.index[:-1])


def window_sum(in_array, window_len):
    """
    Calculates and returns windowed sum of input vector
    :param in_array: input array to be summed
    :type in_array: numpy array
    :param window_len: length of window around each point to be summed
    :type window_len: int
    :return: vector of sums
    :rtype: numpy array
    """
    logger.debug("Summing the data with window length %d" % (window_len))
    w_data = np.convolve(in_array, np.ones(window_len), "valid")
    # Dealing with the special case for endpoints of in_array
    start = np.cumsum(in_array[:window_len - 1])
    start = start[int(np.floor(window_len/2.0))::]
    stop = np.cumsum(in_array[:-window_len:-1])
    stop = stop[int(np.floor(window_len/2.0))-1::][::-1]
    if in_array.shape[0] - w_data.shape[0] - start.shape[0] < stop.shape[0]:
        logger.debug("Window size did not divide easily into input vector length. Adjusting the endpoint values")
        stop = stop[:-1]
    return np.concatenate((start, w_data, stop))


def DeriveWindowSum(data_frame, params=None):
    logger.debug("Starting DeriveWindowSum.")

    if params == None:
        params = {}
        params["func_params"] = {"window_len":("window size for summing",2,True)}
        params["measure_rules"] =  {
                                    "target_measure":("name of the target measure","measure_name",True),
                                    "output_name":("name of returned measure","output_name",True)
                                    }
        return params


    logger.debug("transforming data to %s" % (params["measure_rules"]["output_name"]))
    if "window_len" in params["func_params"]:
        window_len = params["func_params"]["window_len"]
    else:
        window_len = 1
    target_array = data_frame[params["measure_rules"]["target_measure"]].values
    summed_data = window_sum(target_array, window_len)
    return pd.DataFrame(data=summed_data, columns=[params["measure_rules"]["output_name"]], index=data_frame.index)


def scale_data(in_array, scalar):
    """
    Multiply an array by a scaler
    :type in_array: numpy array
    :type scalar: float
    :rtype: numpy array
    """
    return scalar*in_array

def DeriveScaled(data_frame, params=None):
    logger.debug("Starting DeriveScaled.")

    if params == None:
        params = {}
        params["func_params"] = {"scalar":("value to scale data with",1,True)}
        params["measure_rules"] =  {
                                    "target_measure": ("name of the target measure", "measure_name", True),
                                    "output_name": ("name of returned measure", "output_name", True)
                                }
        return params


    logger.debug("transforming data to %s" %(params["measure_rules"]["output_name"]))
    target_array = data_frame[params["measure_rules"]["target_measure"]].values
    scaled_out = scale_data(target_array, params["func_params"]["scalar"])
    return pd.DataFrame(data=scaled_out, columns=[params["measure_rules"]["output_name"]], index=data_frame.index)

def in_box(spatial_array, upper_left, lower_right):
    """
    Given a positional vector and the corners of a box, find which of the point are in the box
    :param spatial_array: spatial input data
    :type spatial_array: N x 2 numpy array
    :param upper_left: coordinates of upper left corner of box
    :type upper_left: 2 x 1 numpy array
    :param lower_right: coordinates of lower right corner of box
    :type lower_right: 2 x 1 numpyh array
    :return: True if a sample point is in the box or False if it is not
    :rtype: N x 1 Boolean numpy array
    """
    return np.logical_and(np.logical_and(spatial_array[:, 0] >= upper_left[0],
                                         spatial_array[:, 0] <= lower_right[0]),
                          np.logical_and(spatial_array[:, 1] <= upper_left[1],
                                         spatial_array[:, 1] >= lower_right[1]))


def DeriveInBox(data_frame, params=None):
    logger.debug("Starting DeriveInBox.")

    if params == None:
        params = {}
        params["func_params"] = {"upper_left_corner":("location of upper left corner",(0,1),True), "lower_right_corner":("location of lower right corner",(1,0),True)}
        params["measure_rules"] = {
                                    "spatial_measure":("name of geo-spatial measure","measure_name",True),
                                    "output_name":("name of returned measure","measure_name",True)
                                    }
        return params


    logger.debug("transforming data to %s" % (params["measure_rules"]["output_name"]))
    position_array = pd.DataFrame(data_frame[params["measure_rules"]["spatial_measure"]].tolist()).values
    box_bool = in_box(position_array, params["func_params"]["upper_left_corner"], params["func_params"]["lower_right_corner"])
    return pd.DataFrame(data=box_bool, columns=[params["measure_rules"]["output_name"]], index=data_frame.index)

#


def compare_threshold(data_array, comparison_operator, comparision_val, absolute_compare=False):
    """
    Fucntion for comparing an array to a values with a binary operator
    :param data_array: input data
    :type data_array: numpy array
    :param comparison_operator: string representation of the binary operator for comparison
    :type comparison_operator: str
    :param comparision_val: The value to be compared against
    :type comparision_val: float
    :param absolute_compare: specifying whether to compare raw value or absolute value
    :type absolute_compare: Boolean
    :return: the indices where the binary operator is true
    :rtype: numpy array
    """
    logger.debug("comparing: %s %d" %(comparison_operator, comparision_val))
    if absolute_compare:
        data_array = np.abs(data_array)
    comparisons= {"==":np.equal, "!=":np.not_equal, ">=":np.greater_equal, "<=":np.less_equal, ">":np.greater, "<":np.less}
    cur_comp = comparisons[comparison_operator]
    match_inds = cur_comp(np.nan_to_num(data_array), comparision_val)
    return match_inds


def DeriveThreshold(data_frame, params=None):
    logger.debug("Starting DeriveThreshold")
    if params == None:
        params = {}
        params["func_params"] = {
            "threshold_value":("value to compare against",0,True),
            "comparison_operator":("one of == != >= <= > <", "==",True),
            "absolute_compare":("whether to compare against absolute value instead of raw value",False,False)}
        params["measure_rules"] = {
                                    "target_measure": ("name of the target measure", "measure_name", True),
                                    "output_name": ("name of returned measure", "output_name", True)
                                }
    logger.debug("transforming data to %s" % (params["measure_rules"]["output_name"]))
    target_array = data_frame[params["measure_rules"]["target_measure"]].values
    threshold_bool = compare_threshold(target_array, params["func_params"]["comparison_operator"],params["func_params"]["threshold_value"],params["func_params"]["absolute_compare"])
    return pd.DataFrame(data=threshold_bool, columns=[params["measure_rules"]["output_name"]], index=data_frame.index)


def logical_combine(array1, array2, combiner):
    """
    Function for creating elementwise AND or OR of two vectors
    :param array1: First array for combination
    :type array1: (n,1) numpy array
    :param array2: Second array for combination
    :type array2: (n,1) numpy array
    :param combiner: "AND" or "OR" specifying which method to combine
    :type combiner: str
    :return: Boolean array combining the two inputs
    :rtype: (n,1) boolean numpy array
    """
    logger.debug(f"Combining with{combiner}")
    combining_func = {"AND":np.logical_and, "OR":np.logical_or}
    return combining_func[combiner](array1, array2)

def DeriveLogicalCombination(data_frame, params=None):
    logger.debug("Starting DeriveLogicalCombination")
    if params == None:
        params = {}
        params["func_params"] = {"combiner":("Either AND or OR string specifying which operator to use","AND",True)}
        params["measure_rules"] = {
                                    "first_measure": ("name of first measure to be combined", "measure_name", True),
                                    "second_measure": ("name of second measure to be combined", "measure_name", True),
                                    "output_name": ("name of returned measure", "output_name", True)
                                }

    logger.debug("Combining {} and {} data to {}".format(params["measure_rules"]["first_measure"],params["measure_rules"]["second_measure"],params["measure_rules"]["output_name"]))
    first_array = data_frame[params["measure_rules"]["first_measure"]].values
    second_array = data_frame[params["measure_rules"]["second_measure"]].values
    print(first_array, second_array)
    combined = logical_combine(first_array, second_array, params["func_params"]["combiner"])
    return pd.DataFrame(data=combined, columns=[params["measure_rules"]["output_name"]],
                            index=data_frame.index)



