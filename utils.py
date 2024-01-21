# -*- coding: utf-8 -*-
"""
Created on Tue Jan  2 11:49:39 2024

@author: dajcs
"""

import os
import sys
import json
import argparse
import numpy as np
from argparse import RawDescriptionHelpFormatter

def get_args(argv):
    '''
    argv : sys.argv
    returns: args : dict
    '''

    # Find the index of '--' token
    # parameters before '--' are for Blender
    try:
        idx = argv.index("--")
        my_args = argv[idx + 1:]  # Arguments after the first '--'
    except ValueError:
        my_args = []

    parser = argparse.ArgumentParser()
    parser = argparse.ArgumentParser(
        description='''
LFW scripts: lf_setup.py and lf_gen.py is used to generate Lens Flare effects using Blender with Lens Flare Wizard add-on.
It is recommended to add Blender program location to the path and start Blender via cmd line from a terminal window, as shown.
The parameters before token "--" are interpreted by Blender\'s python; parameters after token "--" are used by the LFW scripts.
This help message can be displayed by command:
blender --python lf_setup.py -- --help''',
        usage='\nblender [-b] --python lf_[setup|gen].py -- [LFW options]',
        epilog='''
Example: 
blender --python lf_setup.py -- --ref_image LTV.png
can be used to prepare the json file containing the lens flare effects.
This starts with displaying the ref_image LTV.png, on top of it a basic LF effect.  
Add and/or adjust LF elements and save LF to a json file - as described in the terminal window.
Example:
blender --python lf_gen.py -- --lf_params my_lf_params.json --source images --output outimages
is used to add LF effects specified in my_lf_params.json to images in "images" directory and save them to "outimages" directory.''',
        formatter_class=RawDescriptionHelpFormatter
    )
    # listing --background and --python arguments only to be displayed in the help message
    parser.add_argument(
        '-b', '--background',
        default=False,
        action='store_true',
        help='background (headless) blender execution (parameter handled by Blender)'
    )
    parser.add_argument(
        '-P', '--python', 
        help=('path to python script executed by blender (parameter handled by Blender)\n' +
             'Use "--" to separate Blender and LFW script parameters.\n' +
             'After "--" all the parameters will be parsed by the LFW scripts\n')
    )

    # '--'   Delimiter between Blender and LFW script parameters

    parser.add_argument(
        '-ri', '--ref_image',
        default = '',
        help='path to image used as a background for lens flares setup or getting resolution by lf_gen'
    )
    parser.add_argument(
        '-lf', '--lf_params',
        default = 'lf_basic.json',
        help='path to json file storing lens flares settings'
    )
    parser.add_argument(
        '-s', '--source',
        default = '',
        help='path to source directory of original images, or int representing nr of images to generate LF on black background'
    )
    parser.add_argument(
        '-o', '--output',
        default = '',
        help='path to output directory for images with LF, it will be created if it doesn\'t exist'
    )
    parser.add_argument(
        '-rx', '--res_x',
        default = '1920',
        type = int,
        help='resolution X (width, default 1920), of the output images, considered when no ref_image and source is a number (generating LF on black background)'
    )
    parser.add_argument(
        '-ry', '--res_y',
        default = '1080',
        type = int,
        help='resolution Y (height, default 1080) of the output images, considered when no ref_image and source is a number (generating LF on black background)'
    )
    parser.add_argument(
        '-oi', '--outside_image',
        default=20,
        type = int,
        help=('percentage of how far can move the LF effect origin outside the image borders. Default 20% of the image size.')
    )

    args = parser.parse_args(my_args)
    # args, unknown = parser.parse_known_args()
    args = vars(args)  # -> type dict
    # print('unknown =', unknown, '\n')
    return args


try:
    import bpy
# if we're not running in Blender's Python environment print help and exit
except ModuleNotFoundError:
    print('''
    Usage:
        blender --python lf_setup.py -- [options]
        blender --python lf_gen.py -- [options]
    More help:
        blender --python lf_setup.py -- --help
        blender --python lf_gen.py -- --help
''')
    sys.exit()


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


def rand_lf_origin(outside_image_percent):
    '''
    orig_outside_image : int, percentage of image size 
    places 'Light' - therefore LF origin randomly on bg_plane
    '''
    # get bg_plane dimensions
    bg_width, bg_height, _ = bpy.data.objects['FW_BG_Plane'].dimensions
    lf_origin = np.array([bg_width, bg_height]) * (1 + outside_image_percent / 100)  # default +20% if outside image allowed
    lf_origin_middle = lf_origin / 2
    lf_origin *= np.random.rand(2)   # randomize
    lf_orig_x, lf_orig_y = lf_origin - lf_origin_middle    # shift to middle (centered in (0,0))
    # set light x, y coords
    bpy.data.objects['Light'].location = (lf_orig_x, lf_orig_y, 0)
    
    