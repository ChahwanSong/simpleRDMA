#!/usr/bin/env python
# -*- coding: utf-8 -*-
from cmath import inf
import numpy
from collections import OrderedDict
import pickle
import glob
import os
import sys
import copy
import scipy
from telnetlib import IP
from scapy.packet import Packet, bind_layers
from scapy.fields import BitField, ConditionalField
from scapy.all import Ether, IP, UDP, TCP
from scapy.all import sniff
from ast import literal_eval
import numpy as np
import pandas as pd
import copy
pd.set_option('display.max_rows', None)





def get_cdf(v: list):        
    # calculate cdf
    v_sorted = np.sort(v)
    p = 1. * np.arange(len(v)) / (len(v) - 1)
    od = []
    bkt = [0,0,0,0]
    n_accum = 0
    for i in range(len(v_sorted)):
        key = v_sorted[i]/1000.0 
        n_accum += 1
        if bkt[0] == key:
            bkt[1] += 1
            bkt[2] = n_accum
            bkt[3] = p[i]
        else:
            od.append(bkt)
            bkt = [0,0,0,0]
            bkt[0] = key
            bkt[1] = 1
            bkt[2] = n_accum
            bkt[3] = p[i]
    if od[-1][0] != bkt[0]:
        od.append(bkt)
    od.pop(0)

    ret = ""
    for bkt in od:
        var = str(bkt[0]) + " " + str(bkt[1]) + " " + str(bkt[2]) + " " + str(bkt[3]) + "\n"
        ret += var
        
    return ret



###### FOR AGGREGATING IN LOG FOLDER #######

# folder = "/log/143"
# dir_path = os.path.dirname(os.path.realpath(__file__))

# # 1. get all filenames
# filenames = []
# for filename in glob.iglob(dir_path + folder + '/**/*.txt', recursive=True):
#     filenames.append(filename)


# # 2. aggregate all fct data
# fct_data = []
# for filename in filenames:
#     with open(filename, "r") as f:
#         for line in f.readlines():
#             parsed_line = line.replace("\n", "").replace(" ", "").split(",")
#             fct_data.append(float(parsed_line[1]))
            
# # 3. get cdf
# cdf_data = get_cdf(fct_data)

# # 4. save to .dat file
# with open(dir_path + "/cdf.dat", "w") as f:
#     f.write(cdf_data)



###### FOR SINGLE FILE ########
dir_path = os.path.dirname(os.path.realpath(__file__))
# filenames = ["results_reorder_0_pktCount_10_repeat_10000.log",
#                 "results_reorder_0_pktCount_1000_repeat_10000.log",
#                 "results_reorder_1_pktCount_10_repeat_10000.log",
#                 "results_reorder_1_pktCount_1000_repeat_10000.log",
#                 "results_reorder_2_pktCount_10_repeat_10000.log",
#                 "results_reorder_2_pktCount_1000_repeat_10000.log",]


# filenames = ["cx6_results_reorder_0_pktCount_10_repeat_10000.log",
#                 "cx6_results_reorder_0_pktCount_1000_repeat_10000.log",
#                 "cx6_results_reorder_1_pktCount_10_repeat_10000.log",
#                 "cx6_results_reorder_1_pktCount_1000_repeat_10000.log",
#                 "cx6_results_reorder_2_pktCount_10_repeat_10000.log",
#                 "cx6_results_reorder_2_pktCount_1000_repeat_10000.log",]


# filenames = ["cx5_25g_results_reorder_0_pktCount_10_repeat_10000.log",
#                 "cx5_25g_results_reorder_0_pktCount_1000_repeat_10000.log",
#                 "cx5_25g_results_reorder_1_pktCount_10_repeat_10000.log",
#                 "cx5_25g_results_reorder_1_pktCount_1000_repeat_10000.log",
#                 "cx5_25g_results_reorder_2_pktCount_10_repeat_10000.log",
#                 "cx5_25g_results_reorder_2_pktCount_1000_repeat_10000.log",]


# filenames = ["cx5_16352000_25g_results_reorder_1_pktCount_10_repeat_10000.log",
#                 "cx5_16352000_25g_results_reorder_1_pktCount_1000_repeat_10000.log",
#                 "cx5_16352000_25g_results_reorder_2_pktCount_10_repeat_10000.log",
#                 "cx5_16352000_25g_results_reorder_2_pktCount_1000_repeat_10000.log",
#                 ]

# filenames = ["cx6_22301004_25g_results_reorder_0_pktCount_10_repeat_10000.log",
#              "cx6_22301004_25g_results_reorder_0_pktCount_1000_repeat_10000.log",
#              "cx6_22301004_25g_results_reorder_1_pktCount_10_repeat_10000.log",
#                 "cx6_22301004_25g_results_reorder_1_pktCount_1000_repeat_10000.log",
#                 "cx6_22301004_25g_results_reorder_2_pktCount_10_repeat_10000.log",
#                 "cx6_22301004_25g_results_reorder_2_pktCount_1000_repeat_10000.log",
#                 ]

filenames = [
    "cx5_25G_l010_b143_protegoNB.log"
]

filename_to_fct = {}

for filename in filenames:
    fct_result = []
    with open(dir_path + "/" + filename, "r") as f:
        for line in f.readlines():
            parsed_line = line.replace("\n", "").split(",")
            fct_result.append(float(parsed_line[1]))
    filename_to_fct[filename] = fct_result
    print(len(fct_result))
    
    
for filename in filenames:
    cdf_data = get_cdf(filename_to_fct[filename])
    datname = filename.replace(".log", "_cdf.dat")
    with open(dir_path + "/" + datname, "w") as f:
        f.write(cdf_data)