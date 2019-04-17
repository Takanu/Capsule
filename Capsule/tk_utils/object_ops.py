
import bpy
from .select import FocusObject

def DuplicateObject(target):
    """
    Duplicates the given object.
    WARNING - Will also apply the transformation for that object in order to preserve the scale.  </3
    """

    #### Select and make target active
    bpy.ops.object.select_all(action='DESELECT')
    bpy.context.view_layer.objects.active = bpy.data.objects[target.name]
    bpy.ops.object.select_pattern(pattern=target.name)

    # Duplicate the object
    bpy.ops.object.duplicate_move()

    # Now switch the active object to the duplicate
    duplicate = bpy.context.active_object

    # Now set the transform details
    duplicate.rotation_euler = target.rotation_euler
    duplicate.rotation_axis_angle = target.rotation_axis_angle

    # To preserve the scale, it has to be applied.  Sorreh!
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)

def DuplicateObjects(targets):
    """
    Duplicates the given objects.
    WARNING - Will also apply the transformation for the objects in order to preserve the scale.  </3
    """

    #### Select and make target active
    bpy.ops.object.select_all(action='DESELECT')

    for target in targets:
        bpy.context.view_layer.objects.active = bpy.data.objects[target.name]
        bpy.ops.object.select_pattern(pattern=target.name)

    # Duplicate the object
    bpy.ops.object.duplicate_move()

    # Now switch the active object to the duplicate
    duplicate = bpy.context.active_object

    # Now set the transform details
    duplicate.rotation_euler = target.rotation_euler
    duplicate.rotation_axis_angle = target.rotation_axis_angle

    # To preserve the scale, it has to be applied.  Sorreh!
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)

def DeleteObject(target):
    """
    Deletes the given object and removes it from memory.
    """

    # This needs proper data deletion, and all delete operations need to use this
    FocusObject(target)
    bpy.ops.object.delete()

    # Currently removing just in case...
    DeleteObjectByMemory(target)

def DeleteObjectByMemory(target):

    try:
        ob = bpy.data.objects[target.name]

    except:
        ob = None

    if ob != None:
        ob.user_clear()
        bpy.data.objects.remove(ob)

    return

def SwitchObjectMode(newMode, target):
    """
    Forces an object mode switch to the one given, if it isn't already in that mode.
    """
    
    bpy.context.view_layer.objects.active = bpy.data.objects[target.name]
    prevMode = target.mode
    if target.mode != newMode:
        bpy.context.view_layer.objects.active = bpy.data.objects[target.name]
        bpy.ops.object.mode_set(mode=newMode)
        return prevMode

def FindObjectsWithName(context, object_name):
    """
    Attempts to find an object with the given name in the scene of the given context.
    """

    objects_found = []

    for object in context.scene.objects:
        if object.name.find(object_name) != -1:
            objects_found.append(object)

    return objects_found