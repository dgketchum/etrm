# ===============================================================================
# Copyright 2016 dgketchum
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
# ===============================================================================
"""
The purpose of this module is to find a raster file for a specified day.

this module provides (2) function -- find_ndvi, find_prism.
run_distributed_ETRM does all the work

dgketchum 24 JUL 2016
"""

import os
import numpy as np
# from numpy import where, isnan

from app.paths import paths
from recharge import NUMS, PRISM_YEARS
from recharge.raster import Raster


def post_process_ndvi(name, in_path, previous_kcb, band=1, scalar=1.25):
    """
    convert to ndvi to Kcb.

    :param date_object: Datetime object of date.
    :param previous_kcb: Previous day's kcb value.
    :return: numpy array object
    """
    raster = Raster(name, root=in_path, band=band)
    ndvi = raster.masked()
    # ndvi *= 0.0001
    kcb = ndvi * scalar

    if previous_kcb is not None:
        kcb = np.where(np.isnan(kcb) is True, previous_kcb, kcb)
        kcb = np.where(abs(kcb) > 100.0, previous_kcb, kcb)

    return kcb


def get_spline_kcb(date_object, previous_kcb=None):
    """
    Find NDVI image and convert to Kcb.

    :param date_object: Datetime object of date.
    :param previous_kcb: Previous day's kcb value.
    :return: numpy array object
    """
    year = str(date_object.year)

    tail = 'ndvi{}_{:03n}.tif'.format(year, date_object.timetuple().tm_yday)
    path = os.path.join(year, tail)

    raster = Raster(path, root=paths.ndvi_spline)
    ndvi = raster.masked()
    return post_process_ndvi(ndvi, previous_kcb=previous_kcb)


def get_individ_kcb(date_object, previous_kcb=None):
    """
    Find NDVI image and convert to Kcb.

    :param date_object: Datetime object of date.
    :param previous_kcb: Previous day's kcb value.
    :return: numpy array object
    """
    is_walnut_gulch = False

    year = str(date_object.year)
    # Changed for Walnut gulch NDVI naming convention
    # TODO: tiff vs. tif extension on file names breaks mac or PC
    if is_walnut_gulch:
        tail = 'ndvi{}_{:03n}.tif'.format(year, date_object.timetuple().tm_yday)
    else:
        tail = 'NDVI{}_{:02n}_{:02n}.tif'.format(year, date_object.timetuple().tm_mon, date_object.timetuple().tm_mday)

    name = os.path.join(year, tail)
    return post_process_ndvi(name, paths.ndvi_individ, previous_kcb)


def get_individ_ndvi(date_object):
    year = str(date_object.year)
    tail = 'NDVI{}_{:02n}_{:02n}.tif'.format(year,
                                             date_object.timetuple().tm_mon,
                                             date_object.timetuple().tm_mday)

    name = os.path.join(year, tail)
    raster = Raster(name, root=paths.ndvi_individ)
    return raster.masked()


def get_kcb(date_object, previous_kcb=None):
    """
    Find NDVI image and convert to Kcb.

    :param date_object: Datetime object of date.
    :param previous_kcb: Previous day's kcb value.
    :return: numpy array object
    """
    # print date_object
    doy = date_object.timetuple().tm_yday
    year = date_object.year

    if year == 2000:
        band = 1
        # name = '{}_{}.tif'.format(year, doy)
        tail = doy

    elif year == 2001:
        for num in NUMS:
            diff = doy - num
            if 0 <= diff <= 15:
                start = num
                nd = num + 12 if num == 353 else num + 15
                band = diff + 1
                tail = '{}_{}'.format(start, nd)
                # name = '{}_{}_{}.tif'.format(year, start, nd)
                break
    else:
        for i, num in enumerate(NUMS):
            diff = doy - num
            if 0 <= diff <= 15:
                band = diff + 1
                # name = '{}_{}.tif'.format(year, i + 1)
                tail = i + 1
                break

    name = '{}_{}.tif'.format(year, tail)
    return post_process_ndvi(name, paths.ndvi_std_all, previous_kcb, band)


def get_prisms(date, is_reduced = False):
    """
    return all prism variables

    :param date:
    :return: min_temp, max_temp, temp, precip
    """
    min_temp = get_prism(date, variable='min_temp', is_reduced=is_reduced)
    max_temp = get_prism(date, variable='max_temp', is_reduced=is_reduced)
    temp = (min_temp + max_temp) / 2

    precip = get_prism(date, variable='precip', is_reduced=is_reduced)
    precip = np.where(precip < 0, 0, precip)
    return min_temp, max_temp, temp, precip


def get_geo(date_object):
    # TODO: tiff vs. tif extension on file names breaks mac or PC
    tail = '{}{:02n}{:02n}.tif'.format(date_object.year, date_object.month, date_object.day)

    root = os.path.join('precip', '800m_std_all')  # this will need to be fixed
    name = 'PRISMD2_NMHW2mi_{}'.format(tail)
    raster = Raster(name, root=os.path.join(paths.prism, root))

    return raster.geo


def get_prism(date_object, variable='precip', is_reduced = False):
    """
    Find PRISM image.

    :param variable: type of PRISM variable sought
    :type variable: str
    :param date_object: Datetime object of date.
    :return: numpy array object
    """

    is_walnut_gulch = False
    # Changed for Walnut gulch NDVI naming convention

    names = ('precip', 'min_temp', 'max_temp')
    if variable not in names:
        raise NotImplementedError('Invalid PRISM variable name {}. must be in {}'.format(variable, names))

    year = date_object.year
    year_str = str(year)

    # TODO: tiff vs. tif extension on file names breaks mac or PC
    if variable == 'precip':
        if is_reduced:
            root = os.path.join('precip', '800m_std_all')
            tail = '{}{:02n}{:02n}.tif'.format(year, date_object.month, date_object.day)
            name = 'precip_{}'.format(tail)
        else:
            if is_walnut_gulch:
                root = os.path.join('precip', '800m_std_all', year_str)
                tail = '{}{:02n}{:02n}.tiff'.format(year, date_object.month, date_object.day)
                name = 'Walnut_precip_{}'.format(tail)
            else:
                root = os.path.join('precip', '800m_std_all')
                tail = '{}{:02n}{:02n}.tif'.format(year, date_object.month, date_object.day)
                name = 'PRISMD2_NMHW2mi_{}'.format(tail)

    elif variable == 'min_temp':
        if is_reduced:
            root = os.path.join('Temp', 'Minimum_standard')
            tail = '{}{:02n}{:02n}.tif'.format(year, date_object.month, date_object.day)
            name = 'min_temp_{}'.format(tail)
        else:
            if is_walnut_gulch:
                root = os.path.join('Temp', 'Minimum_standard', year_str)
                tail = '{}{:02n}{:02n}.tiff'.format(year, date_object.month, date_object.day)
                name = 'Walnut_MinTemp_{}'.format(tail)
            else:
                root = os.path.join('Temp', 'Minimum_standard')
                tail = '{}{:02n}{:02n}.tif'.format(year, date_object.month, date_object.day)
                if year in PRISM_YEARS:
                    name = 'cai_tmin_us_us_30s_{}'.format(tail)
                else:
                    name = 'TempMin_NMHW2Buff_{}'.format(tail)

    elif variable == 'max_temp':
        if is_reduced:
            root = os.path.join('Temp', 'Maximum_standard')
            tail = '{}{:02n}' \
                   '  {:02n}.tif'.format(year, date_object.month, date_object.day)
            name = 'max_temp_{}'.format(tail)
        else:
            if is_walnut_gulch:
                root = os.path.join('Temp', 'Maximum_standard', year_str)
                tail = '{}{:02n}{:02n}.tiff'.format(year, date_object.month, date_object.day)
                name = 'Walnut_MaxTemp_{}'.format(tail)
            else:
                root = os.path.join('Temp', 'Maximum_standard')
                tail = '{}{:02n}{:02n}.tif'.format(year, date_object.month, date_object.day)
                name = 'TempMax_NMHW2Buff_{}'.format(tail)

    raster = Raster(name, root=os.path.join(paths.prism, root))
    return raster.masked()


def get_penman(date_object, variable='etrs'):
    """
    Find PENMAN image.

    :param variable: type of PENMAN variable sought
    :type variable: str
    :param date_object: Datetime object of date.
    :return: numpy array object
    """
    names = ('etrs', 'rlin', 'rg')
    if variable not in names:
        raise NotImplementedError('Invalid PENMAN variable name {}. must be in {}'.format(variable, names))

    is_walnut_gulch = False
    # Changed for Walnut gulch NDVI naming convention

    year = date_object.year
    tail = '{}_{:03n}.tif'.format(year, date_object.timetuple().tm_yday)

    if variable == 'etrs':
        name = os.path.join('PM{}'.format(year), 'PM_NM_{}'.format(tail)) # default is this one

    elif variable == 'rlin':
        name = os.path.join('PM{}'.format(year), 'RLIN_NM_{}'.format(tail)) # Makes no sense. Not in directory.

    elif variable == 'rg':
        if is_walnut_gulch:
            name = os.path.join('rad{}'.format(year), 'RTOT_NM_{}'.format(tail))
        else:
            name = os.path.join('rad{}'.format(year), 'RTOT_{}'.format(tail))


    raster = Raster(name, root=paths.penman)
    return raster.masked()

# ============= EOF =============================================
# def get_inputs_at_point(coords, full_path):
#     """
#     Finds the point value for any coordinate in a raster object.
#
#     :param coords: Coordinates in format '999999 0000000' UTM
#     :type coords: str
#     :param full_path: Path to raster.
#     :type full_path: str
#     :return: Point value of a raster, float
#     """
#     if type(coords) == str:
#         mx, my = coords.split(' ')
#         mx, my = int(mx), int(my)
#     else:
#         mx, my = coords
#     # print 'coords: {}, {}'.format(mx, my)
#     dataset = gdal.Open(full_path)
#     gt = dataset.GetGeoTransform()
#
#     # print "This here is the full path: {}".format(full_path) # For testing
#     band = dataset.GetRasterBand(1)
#     px = abs(int((mx - gt[0]) / gt[1]))
#     py = int((my - gt[3]) / gt[5])
#     obj = band.ReadAsArray(px, py, 1, 1)
#
#     return obj[0][0]
