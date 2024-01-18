# -*- coding: utf-8 -*-
"""
Created on Tue Jan  2 11:49:39 2024

@author: dajcs
"""

import os
import sys
import json
import argparse

def get_args(argv):

    # Find the index of '--' token
    try:
        idx = argv.index("--")
        my_args = argv[idx + 1:]  # Arguments after the first '--'
    except ValueError:
        my_args = []

    parser = argparse.ArgumentParser()

    # parser.add_argument(
    #     '-b', '--background',
    #     default=False,
    #     action='store_true',
    #     help='background (headless) blender execution'
    # )
    # parser.add_argument(
    #     '-P', '--python', 
    #     help='path to python script executed by blender',
    # )
    parser.add_argument(
        '-bi', '--bg_image',
        default = '',
        help='path to image used as a background for lens flares setup'
    )
    parser.add_argument(
        '-lp', '--lf_params',
        default = 'lf_params.json',
        help='path to json file storing lens flares settings'
    )

    args = parser.parse_args(my_args)
    # args, unknown = parser.parse_known_args()
    args = vars(args)
    # print('type(args):', type(args),'\n') # dict
    # print('unknown =', unknown, '\n')
    return args