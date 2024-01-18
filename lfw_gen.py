
import os
import sys
import json
import argparse

# print(sys.argv)
# ['blender.exe', '--background', '--python', '.\\Documents\\SSP\\LF\\ap.py', '--', 'valaki', 'valahol']

# Find the index of '--' token
try:
    idx = sys.argv.index("--")
    my_args = sys.argv[idx + 1:]  # Arguments after the first '--'
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
    '-i', '--image',
    default = '',
    help='path to image used as a background for lens flares'
)
parser.add_argument(
    '-p', '--params',
    default = 'lf_params.json',
    help='path to json file storing lens flares settings'
)

args = parser.parse_args(my_args)
# args, unknown = parser.parse_known_args()
args = vars(args)
print('args =', args, '\n')
# print('type(args):', type(args),'\n') # dict
# print('unknown =', unknown, '\n')

if '.' not in sys.path:
    sys.path.append('.')

import utils
print('utils.x =', utils.x, '\n')

print('cwd: ', os.getcwd())

import bpy
from bpy import data as D
from bpy import context as C


# camera z coordinate
z_cam = +13.88888931274414  
# background image name with full path
# filepath = r'c:\Users\dajcs\Documents\SSP\LF\images34\img030077.jpg'
filepath = args['image']
if filepath and os.path.exists(filepath):
    filepath = os.path.abspath(filepath)
else:
    filepath = 'Black_BG.png'  # Black_BG.png

# load flares wizard
bpy.ops.flares_wizard.load_props()

# Access the current scene
scene = bpy.context.scene

# Ensure we are in object mode
bpy.ops.object.mode_set(mode='OBJECT')

# Delete the 'Cube'
####################
if "Cube" in bpy.data.objects:
    # Deselect all objects, select 'Cube' and delete
    bpy.ops.object.select_all(action='DESELECT')
    bpy.data.objects['Cube'].select_set(True)
    bpy.ops.object.delete()

# Move 'Camera' to (0,0,z_cam), looking down
############################################
if "Camera" in bpy.data.objects:
    camera = bpy.data.objects['Camera']
    camera.location = (0, 0, z_cam)
    camera.rotation_euler = (0, 0, 0) # in radians


print(f'filepath = {filepath}')

# add Flares Wizard background plane
bpy.ops.flares_wizard.add_background()

# add background image
bpy.ops.flares_wizard.open_image(type="BG", filepath=filepath)
#if filepath:
#    bpy.ops.flares_wizard.open_image(type="BG", filepath=filepath)
#    # match scene resolution to image resolution
#    bpy.ops.flares_wizard.set_scene_resolution()
#else:
#    bpy.ops.flares_wizard.open_image(type="BG")




# get 'FW_BG_Plane' location and scale, move light to (1,1,z_bg + z_cam)
######################################################################
if "FW_BG_Plane" in bpy.data.objects:
    bg_plane = bpy.data.objects['FW_BG_Plane']
    z_bg = bg_plane.location.z

if "Light" in bpy.data.objects:
    light = bpy.data.objects['Light']
    light.location = (1, 1, z_bg + z_cam)
    light.rotation_euler = (0, 0, 0) # in radians



# Switch to Camera View & Rendered shading
###########################################
bpy.context.scene.camera = bpy.data.objects['Camera']
# Find a 3D view area to change context
for area in bpy.context.screen.areas:
    if area.type == 'VIEW_3D':
        # Set the view to the active camera and shading to 'rendered'
        area.spaces.active.region_3d.view_perspective = 'CAMERA'
        area.spaces.active.shading.type = 'RENDERED'
        break



# select 'Light' and make it active
###################################
bpy.ops.object.select_all(action='DESELECT')
obj = bpy.data.objects['Light']
obj.select_set(True)
bpy.context.view_layer.objects.active = obj


with open(args['params']) as f:
    elements =json.load(f)               # list of lf elements

# Add Blank Lens Flare
# bpy.ops.flares_wizard.presets_browser()
bpy.ops.flares_wizard.add_lens_flare()

for i, ele in enumerate(elements):
    #bpy.ops.flares_wizard.add_element(type=ele['type'])  # element type: STREAKS, GHOSTS, SHIMMER,...    
    bpy.context.scene.fw_group.coll[0].ele_index= i
    for prop in ele.keys():
        if prop in ['name', 'ui_name', 'type', 'flare']:
            continue
        elif prop == 'image':
            exec('bpy.context.scene.fw_group.coll[0].elements[i].' + prop + ' = ' + 'bpy.data.images' + str(ele[prop]))
        else:
            exec('bpy.context.scene.fw_group.coll[0].elements[i].' + prop + ' = ' + str(ele[prop]))


# bpy.ops.flares_wizard.add_element(type="STREAKS")
# # bpy.data.scenes['Scene'].fw_group.coll[0].elements[0]
# bpy.ops.flares_wizard.add_element(type="GHOSTS")
# # bpy.data.scenes['Scene'].fw_group.coll[0].elements[1]
# bpy.ops.flares_wizard.add_element(type="SHIMMER")
# # bpy.data.scenes['Scene'].fw_group.coll[0].elements[2]


# streaks_count = 8
bpy.context.scene.fw_group.coll[0].ele_index=0
bpy.context.scene.fw_group.coll[0].elements[0].streaks_count = 3
#bpy.context.scene.fw_group.coll[0]['elements'][0].streaks_count
# ghosts_count = 8
bpy.context.scene.fw_group.coll[0].ele_index=1
bpy.context.scene.fw_group.coll[0].elements[1].ghosts_count = 2

# shimmer_complexity = 8
bpy.context.scene.fw_group.coll[0].ele_index=2
bpy.context.scene.fw_group.coll[0].elements[2].shimmer_complexity = 5



# set world background illumination to 0
bpy.data.worlds["World"].node_tree.nodes["Background"].inputs[0].default_value = (0, 0, 0, 1) # color=black
bpy.data.worlds["World"].node_tree.nodes["Background"].inputs[1].default_value = 0 # strength

# Set Eevee renderig Color Management \ View Transform from 'Filmic' to 'Standard'
bpy.context.scene.view_settings.view_transform = 'Standard'



# Optional: Set output format and file path
bpy.context.scene.render.image_settings.file_format = 'JPEG'  # Set output format
bpy.context.scene.render.filepath = r"render_output.jpg" # Set output path

# Render the scene, save image
# bpy.ops.render.render(write_still = True)

print('Press "N", slect "Lens Flares" in the side menu')
print('Please adjust the Lens Flare effects for your project needs\n')
print('When finished adjustments, save settings by entering the command below into Blender Python console:')
print('import param2json\n')
# __import__('code').interact(local=dict(globals(), **locals()))

