
import os
import sys
import json
import glob
import numpy as np


if '.' not in sys.path:
    sys.path.append('.')

import utils
from lf_setup import prepare_scene

args = utils.get_args(sys.argv)


import bpy
from bpy import data as D
from bpy import context as C

bg_plane = prepare_scene()

if args['lf_params']:
    # load and apply lf_params if specified
    with open(args['lf_params']) as f:
        elements =json.load(f)               # list of lf elements
    utils.apply(elements)
else:
    print('''
    lf_gen.py needs --lf_params to be specified
    more help:
    blender --python lf_gen.py -- --help\n''')
    sys.exit()

if args['odir']:
    if not os.path.exists(args['odir']):
        os.makedirs(args['odir'])
else:
    print('''
    lf_gen.py needs --odir (output directory) to be specified
    more help:
    blender --python lf_gen.py -- --help\n''')
    sys.exit()


if args['sdir']:
    imgs = glob.glob(os.path.join(args['sdir'], '*'))    # all files in sdir
    imgs = [im for im in imgs if os.path.splitext(im)[1] in ['.png', '.jpg', '.jpeg', '.bmp']]  # keep only image files

    for im in imgs:
        # set im as bg_image
        bg_im = os.path.abspath(im)
        # add background image
        bpy.ops.flares_wizard.open_image(type="BG", filepath=bg_im)
        # match scene resolution to image resolution
        bpy.ops.flares_wizard.set_scene_resolution()
        # get bg_plane dimensions
        bg_width, bg_height, _ = bpy.data.objects['FW_BG_Plane'].dimensions
        lf_origin = np.array([bg_width, bg_height]) * (1 + 0.2 * args['outside_image'])  # +20% if outside image allowed
        lf_origin_middle = lf_origin / 2
        lf_origin *= np.random.rand(2)   # randomize
        lf_orig_x, lf_orig_y = lf_origin - lf_origin_middle    # shift to middle (centered in (0,0))
        # set light x, y coords
        bpy.data.objects['Light'].location = (lf_orig_x, lf_orig_y, 0)

        # Set output format and file path
        bpy.context.scene.render.image_settings.file_format = 'JPEG'  # Set output format
        # create output filename
        base_name_with_ext = os.path.basename(bg_im)  # -> e.g. img003077.jpg
        base_name = os.path.splitext(base_name_with_ext)[0] # ---> img003077
        output_fname = os.path.join(os.path.abspath(args['odir']), base_name + '_lf.jpg')
        bpy.context.scene.render.filepath = output_fname # Set output path
        # Render the scene, save image
        bpy.ops.render.render(write_still = True)
