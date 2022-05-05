
# ////////////////////////////////////////////////
# CAPSULE PACK SCRIPTS DEMO
#
#
# Pack Scripts let you edit an export just before it's saved to a file.
# 
# The Blender Python API lets you do anything you'd want to do to create a setup
# just right for your particular workflow in a way I never could with all the interface
# buttons in the world.  Capsule will automate everything else for you, all you need to
# do is add the few things special to how you work!
#
# IMPORTANT INFO
#
# - Use the "Test Export" button when developing scripts to check that they function in
# the way you expect.  If it's a bigger script you might want to test it using the Text
# Editor first, before using Test Export.
#
# -  If some of your exports have the Origin Point set to anything other than
# 'Scene', you'll find that when this script is run the entire scene will have 
# moved in 3D space.  This is how Capsule ensures that an object's origin point is where 
# you want it.
#
# - This script is called twice - once just before an export and once right after.
#
# - A Pack Script is the LAST thing Capsule has to do, everything else including filtering,
# moving objects to the origin point of the scene and anything else has been done.
#
# - Separate Pack Scripts cannot interact with each other, the CAPStatus object that provides
# export information and a way to provide a final export list will be cleared after every
# export operation.



import bpy

context = bpy.context

# CAPStatus is the datablock that provides information on the current export.
# (API explanation pending)
export_status = context.scene.CAPStatus


# The first time the script is called the target_status will equal 'BEFORE_EXPORT'.
# Use this if statement to make changes to the export.

if export_status.target_status == 'BEFORE_EXPORT':

    # Use this to get the objects that Capsule wants to export
    objects = export_status['target_input']
    final_objects = []

    for obj in objects:
        final_objects.append(obj)
    
    # Use this to provide Capsule with the objects you want to export
    # THIS MUST CONTAIN SOMETHING
    export_status['target_output'] = objects


# The second time the script is called the target_status will equal 'AFTER_EXPORT'.
# Use this to revert changes, delete created objects and clean up.

if export_status.target_status == 'AFTER_EXPORT':
    
    # CAPStatus information will be cleared after is this run ready for
    # the next export.
    pass