# ===============================================================================
# Copyright 2018 gabe-parrish
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

# ============= standard library imports ========================
import os
import numpy as np
import matplotlib.pyplot as plt
import pandas as pd

# ============= local library imports ===========================



def parse_file(path, first_col, num_cols):
    """

    :param path:
    :return:
    """
    ascii_unformatted_dict = {}
    ascii_unformatted_dict["good_lines"] = []

    with open(path, 'r') as readfile:
        for line in readfile:
            # print "line ->{}".format(line)

            # kill the spaces, make a list, check by the length of the list.
            line_lst = line.split(" ")
            # print "line list -> {}".format(line_lst)

            #kill spaces

            space_free = list(filter(lambda a: a != '', line_lst))

            # print "space free! -> {}".format(space_free)

            if space_free[0] == first_col and len(space_free) == num_cols:
                bands = space_free
                # print "Headers -> {}".format(headers)
                bands[-1] = bands[-1][:-1]

                ascii_unformatted_dict["bands"] = bands

            elif space_free[0].startswith("F"):
                files = space_free
                files[-1] = files[-1][:-1]
                ascii_unformatted_dict['files'] = files

            elif len(space_free) == num_cols and space_free[0] != first_col:

                goodln = space_free
                # Turn the lines into floats...
                bestln = [float(i) for i in goodln]
                ascii_unformatted_dict["good_lines"].append(bestln)

    print "the full unformatted dict \n", ascii_unformatted_dict

    # use zip to kick ass
    #format the headers list
    headers_list = [ascii_unformatted_dict['bands'][0], ascii_unformatted_dict['bands'][1]]
    for i in ascii_unformatted_dict['files']:
        headers_list.append(i)

    print "headers list", headers_list

    # add the headers list to the ascii_unformatted_dict
    ascii_unformatted_dict['headers'] = headers_list

    print "this should work", ascii_unformatted_dict['headers']

    ascii_dict = {}
    for i in ascii_unformatted_dict['headers']:
        ascii_dict[i] = []

    # zip through each good_lines list and the headers and append the correct value to the list in ascii dict
    for lst in ascii_unformatted_dict['good_lines']:
        for h, val in zip(ascii_unformatted_dict['headers'], lst):
            # print "header", h
            # print "value", val

            ascii_dict[h].append(val)

    print "ascii dict", ascii_dict

    return ascii_dict


def plotter(x, y):
    """

    :param x: your dependent variable
    :param y: your independent variable
    :return:
    """
    # todo - make little gridlines
    # create a variable for ideal ndvi
    ndvi = x
    ideal_etrf = []
    for i in ndvi:
        if i >= 0.8:
            ideal_etrf.append(1)

        elif i < 0.8:
            ideal_etrf.append(i * 1.25)

    # turn your x and y into numpy arrays
    x = np.array(x)
    y = np.array(y)
    ideal_etrf = np.array(ideal_etrf)

    ETrF_vs_NDVI = plt.figure()
    aa = ETrF_vs_NDVI.add_subplot(111)
    aa.set_title('ETrF vs NDVI', fontweight='bold')
    aa.set_xlabel('NDVI', style='italic')
    aa.set_ylabel('ETrF', style='italic')
    aa.scatter(x, y, facecolors='none', edgecolors='blue')
    aa.scatter(x, ideal_etrf, facecolors='none', edgecolors='red')
    plt.minorticks_on()
    # aa.grid(b=True, which='major', color='k')
    aa.grid(b=True, which='minor', color='white')
    plt.tight_layout()
    # TODO - UNCOMMENT AND CHANGE THE PATH TO SAVE THE FIGURE AS A PDF TO A GIVEN LOCATION.
    # plt.savefig(
    #      "/Volumes/SeagateExpansionDrive/jan_metric_PHX_GR/green_river_stack/stack_output/20150728_ETrF_NDVI_gr.pdf")

    plt.show()


def simple_plot(x,y):
    """"""

    # turn your x and y into numpy arrays
    x = np.array(x)
    y = np.array(y)

    plt.scatter(x, y)
    plt.show()


def run_ascii():
    """
    JAN START HERE - G

    Reads in an ascii file from erdas, parses the information and stores it as a numpy array for plotting.
    :return:
    """

    # TODO - CHANGE FOR EVERY NEW ASCII
    # Here's the path to a particular ascii file to start out.
    path = "/Users/Gabe/Desktop/hard_drive_overflow/le70330372000130edc00_x_y_etrf_ndvi_alb_lst.asc"

    # Give the parser the string of the first column header so that the parsing can be done corectly
    first_col = "X"

    # TODO- CHANGE ONLY IF YOU CHANGE THE NUMBER OF VARIABLES IN THE ASCII
    # Give the parser the number of cols
    num_cols = 6

    parsed_dict = parse_file(path, first_col, num_cols)

    # TODO - CHANGE IF YOU WANT TO PLOT SOMETHING DIFFERENT
    # what two variables do you want to plot?
    # in this case since its x = ndvi and y = etrf and based on the ascii file that translates to:
    x = parsed_dict['F2']
    y = parsed_dict['F1']

    # TODO - LEAVE THIS UNCOMMENTED FOR PLOTS OF NDVI AND ETRF
    # this plotter function is customized for NDVI vs ETRF plotting
    plotter(x, y)

    # TODO - UNCOMMENT THESE LINES IF YOU ARENT PLOTTING ETRF AND NDVI AGAINST EACH OTHER
    # # for a simple x, y plot use
    # simple_plot(x, y)

if __name__ == "__main__":

    run_ascii()