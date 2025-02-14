"""Relations between various earthquake parameters - Mw to length, etc.
 Title: conversions.py

  Author:  Peter Row, peter.row@ga.gov.au

  Description: Relations between various earthquake parameters - Mw to length,
  ML to Mw, etc.


  Version: $Revision: 995 $
  ModifiedBy: $Author: dgray $
  ModifiedDate: $Date: 2009-06-30 11:51:34 +1000 (Tue, 30 Jun 2009) $

  Copyright 2007 by Geoscience Australia
"""

from scipy import vectorize, sqrt, sin, minimum, pi, where, asarray, array, \
    exp, log, power, cos, arccos, arcsin, arctan2, zeros, radians, degrees
#import math
from eqrm_code.projections import azimuthal_orthographic_xy_to_ll


def Johnston_01_ML(Mw):
    """
    relationship developed by Arch Johnston, 1989

    coefficients per comms (01)
    """
    C1 = 0.473
    C2 = 0.145
    C3 = 3.45
    return (C1 + (C1 ** 2 - 4 * C2 * (C3 - Mw)) ** 0.5) / (2 * C2)


def Johnston_89_Mw(ML):
    return 3.45 - 0.473 * ML + 0.145 * (ML ** 2)


def obsolete_Wells_and_Coppersmith_94_length(Mw):
    return 10. ** (0.69 * Mw - 3.22)


def modified_Wells_and_Coppersmith_94_area(Mw):
    return 10. ** (Mw - 4.02)


def modified_Wells_and_Coppersmith_94_width(dip, Mw, area, fault_width):
    if Mw > 5.5:
        f = sqrt(sqrt(1 + 2 * (Mw - 5.5) * sin(dip * pi / 180.))) ** -1
    else:
        f = 1.0
    if fault_width is not None:
        return minimum(f * sqrt(area), fault_width)
    else:
        return f * sqrt(area)

modified_Wells_and_Coppersmith_94_width = vectorize(
    modified_Wells_and_Coppersmith_94_width)


def Wells_and_Coppersmith_94(fault_type, Mw, max_width):
    """Calculate the area and widths for ruptures; given fault_type and
    magnitude. The widths are limited by the fault width.


    fault_type     fault type eg 'reverse'
    Mw             magnitudes of the ruptures
    max_width      width of the fault

    Returns an area for the rupture and the max width of rupture.
    """
    if fault_type == "normal":
        area = 10 ** (-2.87 + (0.82 * Mw))
        widthWC = 10 ** (-1.14 + (0.35 * Mw))
    elif fault_type == "reverse":
        area = 10 ** (-3.99 + (0.98 * Mw))
        widthWC = 10 ** (-1.61 + (0.41 * Mw))
    elif fault_type == "strike_slip":
        area = 10 ** (-3.42 + (0.90 * Mw))
        widthWC = 10 ** (-0.76 + (0.27 * Mw))
    elif fault_type == "unspecified":
        area = 10 ** (-3.497 + (0.91 * Mw))
        widthWC = 10 ** (-1.01 + (0.32 * Mw))
    else:
        area = 10 ** (-3.497 + (0.91 * Mw))
        widthWC = 10 ** (-1.01 + (0.32 * Mw))

    width = minimum(widthWC, max_width)
    return area, width


def calc_max_width_in_slab(out_of_dip, slab_width, max_width):
    """Calculate the max width of a rupture within a slab in kms; given
    the slab width, and the out of dip angle.  the returned max width values
    are compared to the calculated width and the fault width, and then
    the mimium value of the 3 is used as the rupture width.

    out_of_dip     out of dip angle in Degrees
    slab_width     width of slab in kms
    max_width      width of the fault

    Returns the max width of ruptures within a slab in kms.
    """
    max_width_in_slab = zeros(len(out_of_dip))

    i = where(out_of_dip >= 180)
    out_of_dip[i] = out_of_dip[i] - 180

    i = where(out_of_dip <= 1)
    max_width_in_slab[i] = max_width

    j = where(((out_of_dip < 90) & (out_of_dip > 1)))
    max_width_in_slab[j] = slab_width / (sin(radians(out_of_dip[j])))

    k = where(out_of_dip == 90)
    max_width_in_slab[k] = slab_width

    k = where((out_of_dip > 90) & (out_of_dip < 179))
    max_width_in_slab[k] = slab_width / (sin(radians(180 - out_of_dip[k])))

    i = where(out_of_dip >= 179)
    max_width_in_slab[i] = max_width

    return max_width_in_slab
# Wells_and_Coppersmith_94 = vectorize(
    # Wells_and_Coppersmith_94)


def depth(depth_top_seismogenic, dip, Mw, fault_width=None):
    """
    depth_top_seismogenic - depth to the top of the seismmogenic region, km.
    dip: dip of the seismmogenic region, degrees
    """
    if fault_width is None:
        fault_width = 15
    rad = pi / 180

    f2 = 1 + ((Mw - 4.0) / 2)
    f2 = where(f2 < 1, 1, f2)
    f2 = where(f2 > 2, 2, f2)

    depth1 = depth_top_seismogenic + f2 / 3 * fault_width * sin(dip * rad)
    depth2 = depth_top_seismogenic + fault_width * \
        sin(dip * rad) - 0.5 * Mw * sin(dip * rad)
    depth = where(depth1 < depth2, depth1, depth2)
    return depth


def calc_depth_to_top(depth, width, delta):
    """Given a fault details, get depth to rupture top.

    depth  depth to fault centroid (km)
    width  width of rupture (km)
    delta  fault dip angle (degrees)

    All three parameters are expected to be numpy arrays.

    Returns Rtor, depth to top of rupture (km)
    Rtor = depth - (width/2)*sin(delta)
    """

    # check dimensions of all three params the same
    try:
        msg = ('Expected depth.shape == width.shape, %s != %s'
               % (str(depth.shape), str(width.shape)))
    except AttributeError:
        raise AssertionError('calc_depth_to_top: expect numpy.array params')
    assert depth.shape == width.shape, msg

    try:
        msg = ('Expected depth.shape == delta.shape, %s != %s'
               % (str(depth.shape), str(delta.shape)))
    except AttributeError:
        raise AssertionError('calc_depth_to_top: expect numpy.array params')
    assert depth.shape == delta.shape, msg

    # convert dip angle in degrees to radians
    delta_rad = delta * pi / 180.0

    # get and return Rtor
    return depth - (width / 2) * sin(delta_rad)


# precalculate constants for convert_Vs30_to_Z10()
Ch_378_7_pow_8 = pow(378.7, 8)
Ch_3_82_div_8 = 3.82 / 8.0


def convert_Vs30_to_Z10(Vs30):
    """Convert a Vs30 (m/s) value to an estimated Z1.0 (km) value.

    This function will handle both scalar and scipy array values of Vs30.

    Formula taken from equation (1) of:
    Chiou.B.S.-J., Youngs R.R., 2008 An NGA Model for the Average Horizontal
    Component of Peak Ground Motion and Response Spectra,
    Earthquake Spectra 24, 173-215.
    """

    Z10_m = exp(28.5 - Ch_3_82_div_8 * log(power(Vs30, 8) + Ch_378_7_pow_8))

    return Z10_m / 1000.0


def convert_Z10_to_Z25(Z10):
    """Convert a Z1.0 value (km) to a Z2.5 value (km).

    This function will handle both scalar and scipy array values of Z10.

    Formula taken from equation (6.3) of:
    Campbell-Bozorgnia NGA Ground Motion Relations for the Geometric Mean
    Horizontal Component of Peak and Spectral Ground Motion Parameters.
    Kenneth W. Campbell and Yousef Bozorgnia, PEER 2007/02.
    """

    return 0.519 + 3.595 * Z10


def convert_Vs30_to_Z25(Vs30):
    """A combined function to get Z2.5 from Vs30."""

    return convert_Z10_to_Z25(convert_Vs30_to_Z10(Vs30))


def AS08_convert_Vs30_to_Z10_Z25(Vs30):
    """Convert a Vs30 (m/s) value to estimated Z1.0 & Z2.5 (km) values
    according to the AS08 model code from site below.

    Vs30  shear wave speed at depth of 30m (m/s)

    Returns a tuple (Z1.0, Z2.5), both values in km.

    This function will handle both scalar and scipy array values of Vs30.

    This code is taken from the nga_gm_tmr.for program found at
    [http://www.daveboore.com/software_online.html].
    """

    AS08_Z10 = exp(6.745 - 1.35 * log(Vs30 / 180.0))
    AS08_Z10 = where(
        Vs30 > 500.0,
        exp(5.394 - 4.48 * log(Vs30 / 500.0)),
        AS08_Z10)
    AS08_Z10 = where(Vs30 < 180.0, exp(6.745), AS08_Z10)

    AS08_Z25 = 0.519 + 3.595 * (AS08_Z10 / 1000.0)

    return (AS08_Z10, AS08_Z25)


def azimuth_of_trace(start_lat, start_lon, end_lat, end_lon):
    """Calculate a trace azimuth given start and end positions.

    start_lat  latitude of start point
    start_lon  longitude of start point
    end_lat    latitude of end point
    end_lon    longitude of end point

    Returns azimuth at start point in degrees, in range [0, 360).
    """

    dx = end_lon - start_lon
    dy = end_lat - start_lat
    azimuth = arctan2(dx * cos(start_lat * pi / 180.0), dy) * 180.0 / pi
    if azimuth < 0.0:
        azimuth += 360.0

    return azimuth


def calc_ll_dist(lat1, lon1, lat2, lon2):
    """Calculate a length in kms given start and end positions.

    lat1  latitude of start point
    lon1  longitude of start point
    lat2    latitude of end point
    lon2    longitude of end point

    Returns length from start point in kms.
    """
    R = 6371
    dLat = radians(abs(lat2 - lat1))
    dLon = radians(abs(lon2 - lon1))
    a = (sin(dLat / 2) * sin(dLat / 2) +
         cos(radians(lat1)) * cos(radians(lat2)) *
         sin(dLon / 2) * sin(dLon / 2))
    c = 2 * arctan2(sqrt(a), sqrt(1 - a))
    return R * c


def calc_fault_area(lat1, lon1, lat2, lon2, depth_top, depth_bottom, dip):
    """Calculate the area of a fault in kms given the trace, dip and depth
       top and bottom.

    lat1          latitude of start point
    lon1          longitude of start point
    lat2          latitude of end point
    lon2          longitude of end point
    depth_top     depth to the top of the seismogenic zone
    depth_bottom  depth to the bottom of the seismogenic zone
    dip           angle of dip of the fault in decimal degrees

    Returns area of fault in kms.
    """
    fault_length = calc_ll_dist(lat1, lon1, lat2, lon2)
    fault_width = (depth_bottom - depth_top) / sin(radians(dip))
    fault_area = fault_length * fault_width
    return fault_area


def calc_fault_width(depth_top, depth_bottom, dip):
    """Calculate the width of a fault in kms given the dip and depth top and
    bottom.


    depth_top     depth to the top of the seismogenic zone
    depth_bottom  depth to the bottom of the seismogenic zone
    dip           angle of dip of the fault in decimal degrees

    Returns width of fault in kms.
    """
    fault_width = (depth_bottom - depth_top) / sin(radians(dip))
    return fault_width


def calc_fault_length(lat1, lon1, lat2, lon2):
    """Calculate the length of a fault in kms given the start and end coords
       of the fault trace.

    lat1          latitude of start point
    lon1          longitude of start point
    lat2          latitude of end point
    lon2          longitude of end point

    Returns length of fault in kms.
    """
    fault_length = calc_ll_dist(lat1, lon1, lat2, lon2)
    return fault_length


def get_new_ll(lat1, lon1, azimuth, distance_kms):
    """Calculate the lat, lon coords a spefied distance along a fault trace,
    given the start coords the azimuth and the distance along the trace.

    lat1          latitude of start point
    lon1          longitude of start point
    azimuth       azimuth
    distance_kms  distance in kms

    Returns the lat, lon coords a spefied distance along a fault trace.
    """
    x = distance_kms  # cos(azimuth)*distance_kms
    y = 0.0  # sin(azimuth)*distance_kms
    return azimuthal_orthographic_xy_to_ll(x, y, lat1, lon1, azimuth)


def switch_coords(start_lat, start_lon, end_lat, end_lon):
    """flips the start and end coords of a trace.

    start_lat          latitude of start point
    start_lon          longitude of start point
    end_lat            latitude of end point
    end_lon            longitude of end point

    Returns the lat, lon of the 2 coords in the reverse order.
    """
    return(end_lat, end_lon, start_lat, start_lon)


def calc_new_rupture_trace_lower_slab(top_dip, depth_bottom, top_trace_lat_s,
                                      top_trace_lon_s, top_trace_lat_e,
                                      top_trace_lon_e, lower_dip,):
    """Calculates the trace for a lower slab so that it matches the bottom
    of the upper slab.

    top_dip                  dip of top slab
    depth_bottom             depth of the bottom of top slab
    top_trace_lat_s          latitude of start point - top slab
    top_trace_lon_s          longitude of start point - top slab
    top_trace_lat_e          latitude of end point - top slab
    top_trace_lon_e          longitude of end point - top slab
    lower_dip

    Returns low_trace_lat_s, low_trace_lon_s, low_trace_lat_e,low_trace_lon_e.
    """
    azimuth = azimuth_of_trace(
        top_trace_lat_s, top_trace_lon_s, top_trace_lat_e,
        top_trace_lon_e)

    y1 = depth_bottom * ((cos(radians(top_dip))) /
                         (sin(radians(top_dip))))
    (temp_trace_lat_s, temp_trace_lon_s) = \
        azimuthal_orthographic_xy_to_ll(0, y1, top_trace_lat_s,
                                        top_trace_lon_s,
                                        azimuth)
    (temp2_trace_lat_s, temp2_trace_lon_s) = \
        get_new_ll(top_trace_lat_s,
                   top_trace_lon_s,
                   azimuth + 90, y1)
    (temp_trace_lat_e, temp_trace_lon_e) = \
        azimuthal_orthographic_xy_to_ll(0, y1, top_trace_lat_e,
                                        top_trace_lon_e,
                                        azimuth)
    (temp2_trace_lat_e, temp2_trace_lon_e) = \
        get_new_ll(top_trace_lat_e,
                   top_trace_lon_e,
                   azimuth + 90, y1)
    y2 = depth_bottom * ((cos(radians(lower_dip))) /
                         (sin(radians(lower_dip))))
    y = y1 - y2

    (low_trace_lat_s, low_trace_lon_s) = \
        azimuthal_orthographic_xy_to_ll(0, y, top_trace_lat_s,
                                        top_trace_lon_s,
                                        azimuth)

    (low_trace_lat_e, low_trace_lon_e) = \
        azimuthal_orthographic_xy_to_ll(0, y, top_trace_lat_e,
                                        top_trace_lon_e,
                                        azimuth)
    return low_trace_lat_s, low_trace_lon_s, low_trace_lat_e, low_trace_lon_e


def obsolete_calc_azimuth(lat1, lon1, lat2, lon2):
    """NOT USED
       Calculate a trace azimuth given start and end positions.

    lat1          latitude of start point
    lon1          longitude of start point
    lat2          latitude of end point
    lon2          longitude of end point

    Returns azimuth at start point in degrees, in range [0, 360).
    """
    lat1 = radians(lat1)
    lon1 = radians(lon1)
    lat2 = radians(lat2)
    lon2 = radians(lon2)
    numerator = sin(lon1 - lon2) * cos(lat2)
    denominator = sin(arccos((sin(lat2) * sin(lat1)) + (cos(lat1) * cos(lat2) *
                                                        cos(lon2 - lon1))))
    azimuth = degrees(arcsin(numerator / denominator))
    return azimuth


def obsolete_calc_azimuth2(lat1, lon1, lat2, lon2):
    """NOT USED
       Calculate a trace azimuth given start and end positions.

    lat1          latitude of start point
    lon1          longitude of start point
    lat2          latitude of end point
    lon2          longitude of end point

    Returns azimuth at start point in degrees, in range [0, 360).
    """

    x = calc_ll_dist(lat1, lon1, lat1, lon2)
    y = calc_ll_dist(lat1, lon1, lat2, lon1)
    if y == 0:
        azimuth = 90
    elif x == 0:
        azimuth = 0
    else:
        azimuth = degrees(arctan2(x, y))
    return azimuth


def obsolete_calc_azimuth3(lat1, lon1, lat2, lon2):
    """NOT USED
       Calculate a trace azimuth given start and end positions.

    lat1          latitude of start point
    lon1          longitude of start point
    lat2          latitude of end point
    lon2          longitude of end point

    Returns azimuth at start point in degrees, in range [0, 360).
    """

    x = (lon1 - lon2) * (cos(lat1))
    y = lat1 - lat2
    if y == 0:
        azimuth = 90
    elif x == 0:
        azimuth = 0
    else:
        azimuth = degrees(arctan2(x, y))
    return azimuth

###################
# END OF FUNCTIONS#
###################

"""No functions past this step will be included in the table"""
__local_functions = locals().copy()  # all the functions in the local namespace
# Note that this is a copy, otherwise __local_functions would point to itself

conversion_functions = {}
for function_name in __local_functions.keys():
    # for all functions in the local namespace

    if not function_name.startswith('__'):  # If it's not private
        function = __local_functions[function_name]
        conversion_functions[function_name] = function
