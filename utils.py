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
    # parameters before '--' are for Blender
    try:
        idx = argv.index("--")
        my_args = argv[idx + 1:]  # Arguments after the first '--'
    except ValueError:
        my_args = []

    parser = argparse.ArgumentParser()
    # parser.add_argument(
    #     '-b', '--background',
    #     default=True,
    #     action='store_true',
    #     help='background (headless) blender execution'
    # )
    # parser.add_argument(
    #     '-P', '--python', 
    #     help='path to python script executed by blender',
    # )
    # '--'
    parser.add_argument(
        '-bi', '--bg_image',
        default = '',
        help='path to image used as a background for lens flares setup'
    )
    parser.add_argument(
        '-lp', '--lf_params',
        default = '',
        help='path to json file storing lens flares settings'
    )

    args = parser.parse_args(my_args)
    # args, unknown = parser.parse_known_args()
    args = vars(args)  # -> type dict
    # print('unknown =', unknown, '\n')
    return args


import bpy

def apply(elements):
    '''
    elements : list of LF elements
    applies the settings to element properties
    '''


    for i, ele in enumerate(elements):
        bpy.ops.flares_wizard.add_element(type=ele['type'])  # element type: STREAKS, GHOSTS, SHIMMER,...    
        bpy.context.scene.fw_group.coll[0].ele_index= i
        print(f'\ni = {i}')
        print(f'ele = {list(ele.items())[:4]}\n')
        for prop in ele.keys():
            if prop in ['name', 'ui_name', 'type', 'flare']:
                continue
            elif prop == 'image':
                if not ele['image'][0] in bpy.data.images:
                    # texture_path in Windows, on Linux 'Users' -> 'home' (probably)
                    texture_path = os.path.join( 
                        [p for p in sys.path if 'Users' in p and p.endswith('addons')][0], 
                                                                                'FlaresWizard', 'Textures')
                    filepath = os.path.join(texture_path, ele['image'][0])
                    bpy.ops.flares_wizard.open_image(type="ELEMENT", filepath=filepath)
                print(f'bpy.context.scene.fw_group.coll[0].elements[{i}].{prop} = bpy.data.images{ele[prop]}')
                exec(f'bpy.context.scene.fw_group.coll[0].elements[{i}].{prop} = bpy.data.images{ele[prop]}')
            else:
                print(f'bpy.context.scene.fw_group.coll[0].elements[{i}].{prop} = {ele[prop]}')
                try:
                    exec(f'bpy.context.scene.fw_group.coll[0].elements[{i}].{prop} = {ele[prop]}')
                except TypeError:
                    print(f'bpy.context.scene.fw_group.coll[0].elements[{i}].{prop} = "{ele[prop]}"')
                    exec(f'bpy.context.scene.fw_group.coll[0].elements[{i}].{prop} = "{ele[prop]}"')


def save(fname='lf_params.json'):
    '''
    fname : string, optional, default: 'lf_params.json'
    saves current LF elements to specified/default json file
    '''
    x = str([ x.to_dict() for x in bpy.context.scene.fw_group.coll[0]['elements']]).replace('bpy.data.images','')
    # js = json.dumps(eval(x), indent=4)
    
    try:
        with open(fname, 'w') as f:
            json.dump(eval(x), f, indent=4)
        print(f'Lens Flare parameters saved to file "{fname}"\n')
    except Exception as e:
        print(f"An error occurred:\n\n{e}\n\nTry again...")

