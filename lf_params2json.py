# -*- coding: utf-8 -*-
"""
Created on Thu Jan 18 11:01:34 2024

@author: dajcs
"""
import bpy
import json

x = str([ x.to_dict() for x in bpy.context.scene.fw_group.coll[0]['elements']]).replace('bpy.data.images','')
# js = json.dumps(eval(x), indent=4)
fname = 'lf_params.json'

with open('lf_params.json', 'w') as f:
    json.dump(eval(x), f, indent=4)

print('Lens Flare parameters saved to file "lf_params.json"\n')