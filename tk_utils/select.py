
# Because selections in Blender can be weird this module provides methods to ensure
# selections are being performed the right way

import bpy

# ////////////////////////////////////////
# OBJECTS

# TODO: The forcing of hide_set and hide_select can cause behaviour problems.
# but I can't change this without knowing how much depended on this behaviour.
# oh no.

def FocusObject(target):
    """
    Focuses the given target in the 3D View while deselecting all other objects.
    """

    # If the target isnt visible, MAKE IT VISIBLE.
    if target.hide_get() is True:
        target.hide_set(False)

    if target.hide_select is True:
        target.hide_select = False

    # If the mode is not object, we have to change it before using the
    # Select All command
    bpy.context.view_layer.objects.active = bpy.data.objects[target.name]

    prevMode = ''
    if target.mode != 'OBJECT':
        prevMode = target.mode
        bpy.context.view_layer.objects.active = bpy.data.objects[target.name]
        bpy.ops.object.mode_set(mode = 'OBJECT')

    #### Select and make target active
    bpy.ops.object.select_all(action = 'DESELECT')
    bpy.context.view_layer.objects.active = bpy.data.objects[target.name]
    bpy.ops.object.select_pattern(pattern=target.name)

    # Set the mode back
    if prevMode != '':
        bpy.ops.object.mode_set(mode = prevMode)




def SelectObject(target, force_select = False):
    """
    Selects the given target in the 3D View.  This does not make the object active.
    - force_select: If true the target will be selected regardless of any hide settings it has, otherwise it won't.
    """

    # #print('selecting... ', target)

    if force_select == False:
        if target.hide_get() is True and target.hide_select is True:
            return

    # If the target isnt visible, MAKE IT VISIBLE.
    if target.hide_get() is True:
        target.hide_set(False)

    if target.hide_select is True:
        target.hide_select = False

    # #print('attempting to select... ', target)
    # #print('attempting to select... ', target)
    # #print('attempting to select... ', target)

    target.select_set(True)


def ActivateObject(target):
    """
    Makes the given object the one that is currently active in the 3D view.
    """
    # If the target isnt visible, MAKE IT VISIBLE.
    if target.hide_get() is True:
        target.hide_set(False)

    if target.hide_select is True:
        target.hide_select = False

    bpy.context.view_layer.objects.active = bpy.data.objects[target.name]


# ////////////////////////////////////////
# COLLECTIONS

# just a stub, I dont think I can select multiple collections </3


# ////////////////////////////////////////
# STATES


def SaveObjectSelections():
    """
    Records the current active and selected objects and returns a dictionary.
    """

    record = {}
    if bpy.context.active_object is not None:
        record['active'] = bpy.context.active_object
    
    record['selected'] = bpy.context.selected_objects

    return record


def RestoreObjectSelections(record):
    """
    Restores a previously-recorded selection set.
    """

    if record['active'] is not None:
        ActivateObject(record['active'])
    
    for item in record['selected']:
        SelectObject(item)