
import os
import sys
import json


if '.' not in sys.path:
    sys.path.append('.')

import utils

args = utils.get_args(sys.argv)

import bpy
from bpy import data as D
from bpy import context as C





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
# camera z coordinate
z_cam = +13.88888931274414  
if "Camera" in bpy.data.objects:
    camera = bpy.data.objects['Camera']
    camera.location = (0, 0, z_cam)
    camera.rotation_euler = (0, 0, 0) # in radians


# Add background image
######################
# background image fname with full path or "Black_BG.png"
bg_filepath = args['bg_image']
if bg_filepath and os.path.exists(bg_filepath):
    bg_filepath = os.path.abspath(bg_filepath)
else:
    bg_filepath = 'Black_BG.png'  # Black_BG.png

# add Flares Wizard background plane
bpy.ops.flares_wizard.add_background()
# add background image
bpy.ops.flares_wizard.open_image(type="BG", filepath=bg_filepath)
# match scene resolution to image resolution
bpy.ops.flares_wizard.set_scene_resolution()


# get 'FW_BG_Plane' location and scale, move light to (1,1,z_bg + z_cam)
######################################################################
if "FW_BG_Plane" in bpy.data.objects:
    bg_plane = bpy.data.objects['FW_BG_Plane']
    z_bg = bg_plane.location.z
    bg_dim = D.objects['FW_BG_Plane'].dimensions  # Vector((10.001999855041504, 7.501999855041504, 0.0))

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



# bpy.ops.flares_wizard.presets_browser()
bpy.ops.flares_wizard.add_lens_flare()

bpy.ops.flares_wizard.add_element(type="STREAKS")
# bpy.data.scenes['Scene'].fw_group.coll[0].elements[0]
bpy.context.scene.fw_group.coll[0].ele_index=0
bpy.context.scene.fw_group.coll[0].elements[0].streaks_count = 3

bpy.ops.flares_wizard.add_element(type="GHOSTS")
# bpy.data.scenes['Scene'].fw_group.coll[0].elements[1]
bpy.context.scene.fw_group.coll[0].ele_index=1
bpy.context.scene.fw_group.coll[0].elements[1].ghosts_count = 2

bpy.ops.flares_wizard.add_element(type="SHIMMER")
# bpy.data.scenes['Scene'].fw_group.coll[0].elements[2]
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

print('\nPress "N", slect "Lens Flares" in the side menu')
print('Please adjust the Lens Flare effects for your project needs\n')
print('When finished adjustments, select Scripting workspace (top menu right')
print('Save settings by entering the command below into Blender Python console (left middle window)')
print('import param2json\n')


