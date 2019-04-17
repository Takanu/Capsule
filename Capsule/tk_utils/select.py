import bpy

def FocusObject(target):
    """
    Focuses the given target in the 3D View while deselecting all other objects.
    """
    # If the target isnt visible, MAKE IT VISIBLE.
    if target.hide_viewport is True:
        target.hide_viewport = False

    if target.hide_select is True:
        target.hide_select = False

    # If the mode is not object, we have to change it before using the
    # Select All command
    bpy.context.view_layer.objects.active = bpy.data.objects[target.name]

    prevMode = ''
    if target.mode != 'OBJECT':
        prevMode = target.mode
        bpy.context.view_layer.objects.active = bpy.data.objects[target.name]
        bpy.ops.object.mode_set(mode='OBJECT')

    #### Select and make target active
    bpy.ops.object.select_all(action='DESELECT')
    bpy.context.view_layer.objects.active = bpy.data.objects[target.name]
    bpy.ops.object.select_pattern(pattern=target.name)

    # Set the mode back
    if prevMode != '':
        bpy.ops.object.mode_set(mode=prevMode)

def SelectObject(target):
    """
    Selects the given target in the 3D View.  This does not make the object active.
    """
    # If the target isnt visible, MAKE IT VISIBLE.
    if target.hide_viewport is True:
        target.hide_viewport = False

    if target.hide_select is True:
        target.hide_select = False

    target.select_set(True)

def ActivateObject(target):
    """
    Makes the given object the one that is currently active in the 3D view.
    """
    # If the target isnt visible, MAKE IT VISIBLE.
    if target.hide_viewport is True:
        target.hide_viewport = False

    if target.hide_select is True:
        target.hide_select = False

    bpy.context.view_layer.objects.active = bpy.data.objects[target.name]