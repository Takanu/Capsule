
# ////////////////////////////////////////////////
# CAPSULE OVERRIDE DEMO
#
#
# Overrides let you adjust the objects that are about to export in any way you wish.
# The Blender Python API lets you do 99.9% of the things you could do using it's interface
# which makes Overrides a great way to remove any tedious custom setups you might
# need to perform on an export.
#
# IMPORTANT INFO
#
# - Create and test your scripts without Capsule first so you check they do what
# you expect them to.
# 
#
# -  If some of your exports have the Origin Point set to anything other than
# 'Scene', when this script is run the entire scene will have moved in 3D space.  
# This is how Capsule ensures that an object's origin point is where you want it.
#
#

import bpy

context = bpy.context

# CAPStatus is the datablock that provides information on the current export.
export_status = context.scene.CAPStatus


# This is called just before Capsule will save Export Targets to a file.
# This is the LAST thing Capsule has to do, everything else including filtering,
# moving objects to the origin point of the scene and anything else has been done.
if export_status.target_status == 'BEFORE_EXPORT':

    # Use this to get the objects that Capsule wants to export
    # objects = export_status['target_input']
    
    
    # Use this to provide Capsule with the objects you want to export
    # THIS MUST CONTAIN SOMETHING
    # export_status['target_output'] = your_final_export_items
    pass
    
    
if export_status.target_status == 'AFTER_EXPORT':
    # this is called just after exporting, clean up the operations you
    # performed here.
    
    # CAPStatus information will be cleared after is this run ready for
    # the next export.
    pass