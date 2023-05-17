
import bpy
from math import pi, radians, degrees
from mathutils import Vector

from .select import FocusObject
from .object_ops import SwitchObjectMode, Find3DViewContext

#//////////////////// - BASIC DEFINITIONS - ///////////////////////

def FindWorldSpaceObjectLocation(context, target):
    """
    Finds the given object location in world space, NO MATTER WHAT THE CIRCUMSTANCES.
    """

    # Preserve the current 3D cursor
    cursor_loc = bpy.data.scenes[bpy.context.scene.name].cursor.location
    previous_cursor_loc = [cursor_loc[0], cursor_loc[1], cursor_loc[2]]

    override = Find3DViewContext()

    with context.temp_override(window = override['window'], area = override['area'], 
            region = override['region']):
        
        # Calculate the translation vector using the 3D cursor
        FocusObject(target)
        bpy.ops.view3d.snap_cursor_to_selected()
        cursor_location = bpy.data.scenes[bpy.context.scene.name].cursor.location

        # Because vectors are pointers, we need to keep regenerating them
        cursor_loc_copy = Vector((cursor_location[0], cursor_location[1], cursor_location[2]))

        # Restore the original cursor location and matrix
        bpy.data.scenes[bpy.context.scene.name].cursor.location = previous_cursor_loc

    return cursor_loc_copy

def FindWorldSpaceBoneLocation(target, context, bone):
    """
    Finds the given bone location in world space, NO MATTER WHAT THE CIRCUMSTANCES.
    """

    # Preserve the current 3D cursor
    cursor_loc = bpy.data.scenes[bpy.context.scene.name].cursor.location
    previous_cursor_loc = [cursor_loc[0], cursor_loc[1], cursor_loc[2]]

    override = Find3DViewContext()

    with context.temp_override(window = override['window'], area = override['area'], 
            region = override['region']):

        # Calculate the translation vector using the 3D cursor
        bpy.ops.object.select_all(action= 'DESELECT')
        prev_mode = SwitchObjectMode('POSE', target)
        bpy.data.objects[target.name].data.bones.active = bpy.data.objects[target.name].pose.bones[bone.name].bone
        bpy.ops.view3d.snap_cursor_to_selected()
    
    cursor_location = Vector((0.0, 0.0, 0.0))
    cursor_location = bpy.context.scene.cursor.location

    # Because vectors are pointers, we need to keep regenerating them
    cursor_loc_copy = Vector((0.0, 0.0, 0.0))
    cursor_loc_copy[0] = cursor_location[0]
    cursor_loc_copy[1] = cursor_location[1]
    cursor_loc_copy[2] = cursor_location[2]

    SwitchObjectMode(prev_mode, target)

    # Restore the original cursor location and matrix
    bpy.data.scenes[bpy.context.scene.name].cursor.location = previous_cursor_loc

    return cursor_loc_copy
