
import os
import sys
import json
import glob


if '.' not in sys.path:
    sys.path.append('.')

import utils
from lf_setup import prepare_scene

args = utils.get_args(sys.argv)


import bpy

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

if args['output']:
    if not os.path.exists(args['output']):  # create output directory if it doesn't exist
        os.makedirs(args['output'])
else:
    print('''
    lf_gen.py needs --output to be specified
    more help:
    blender --python lf_gen.py -- --help\n''')
    sys.exit()

if args['source']:
    imgs = glob.glob(os.path.join(args['source'], '*'))    # all files in source directory
    imgs = [im for im in imgs if os.path.splitext(im)[1] in ['.png', '.jpg', '.jpeg', '.bmp']]  # keep only image files
    if not imgs:
        try:
            nr_img = int(args['source'])
        except ValueError:
            print(f"\nThe specified --source {args['source']} has no images and it can't convert to integer\n")
            sys.exit()
else:
    print('''
    lf_gen.py needs --source to be specified
    more help:
    blender --python lf_gen.py -- --help\n''')
    sys.exit()


if imgs:
    # add LF to images in --source directory
    for im in imgs:
        # set im as bg_image
        bg_im = os.path.abspath(im)
        # add background image
        bpy.ops.flares_wizard.open_image(type="BG", filepath=bg_im)
        # match scene resolution to image resolution
        bpy.ops.flares_wizard.set_scene_resolution()

        # randomize lf origin
        utils.rand_lf_origin(args['outside_image'])

        # create output filename
        base_name_with_ext = os.path.basename(bg_im)  # -> e.g. img003077.jpg
        base_name = os.path.splitext(base_name_with_ext)[0] # ---> img003077
        output_fname = os.path.join(os.path.abspath(args['output']), base_name + '_lf.jpg')
        # Set output path
        bpy.context.scene.render.filepath = output_fname 
        # Render the scene, save image
        bpy.ops.render.render(write_still = True)

else:
    # generate nr_img LF effects and save them on black background
    if not args['ref_image']:
        bpy.context.scene.render.resolution_x = args['res_x']   # width in pixels, default 1920
        bpy.context.scene.render.resolution_y = args['res_y']   # height in pixels, default 1080

    nr_digit = len(str(nr_img - 1))
    for i in range(nr_img):
        # randomize lf origin
        utils.rand_lf_origin(args['outside_image'])

        # create output filename
        fname = 'lf_' + str(i).zfill(nr_digit) + '.jpg'
        output_fname = os.path.join(os.path.abspath(args['output']), fname)
        # Set output path
        bpy.context.scene.render.filepath = output_fname 
        # Render the scene, save image
        bpy.ops.render.render(write_still = True)

