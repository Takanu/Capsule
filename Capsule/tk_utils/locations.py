import bpy, bmesh, time
from math import pi, radians, degrees
from mathutils import Vector

from .select import FocusObject
from .object_ops import SwitchObjectMode

#//////////////////// - BASIC DEFINITIONS - ///////////////////////

def FindWorldSpaceObjectLocation(target, context):
    """
    Finds the given object location in world space, NO MATTER WHAT THE CIRCUMSTANCES.
    """

    # Preserve the current 3D cursor
    cursor_loc = bpy.data.scenes[bpy.context.scene.name].cursor_location
    previous_cursor_loc = [cursor_loc[0], cursor_loc[1], cursor_loc[2]]

    # Calculate the translation vector using the 3D cursor
    FocusObject(target)
    bpy.ops.view3d.snap_cursor_to_selected()
    cursor_location = bpy.data.scenes[bpy.context.scene.name].cursor_location

    # Because vectors are pointers, we need to keep regenerating them
    cursorLocCopy = Vector((cursor_location[0], cursor_location[1], cursor_location[2]))

    # Restore the original cursor location and matrix
    bpy.data.scenes[bpy.context.scene.name].cursor_location = previous_cursor_loc

    return cursorLocCopy

def FindWorldSpaceBoneLocation(target, context, bone):
    """
    Finds the given bone location in world space, NO MATTER WHAT THE CIRCUMSTANCES.
    """

    # Preserve the current 3D cursor
    cursor_loc = bpy.data.scenes[bpy.context.scene.name].cursor_location
    previous_cursor_loc = [cursor_loc[0], cursor_loc[1], cursor_loc[2]]

    # Calculate the translation vector using the 3D cursor
    bpy.ops.object.select_all(action='DESELECT')
    prevMode = SwitchObjectMode('POSE', target)
    bpy.data.objects[target.name].data.bones.active = bpy.data.objects[target.name].pose.bones[bone.name].bone
    bpy.ops.view3d.snap_cursor_to_selected()
    cursor_location = Vector((0.0, 0.0, 0.0))

    for area in context.screen.areas:
        if area.type == 'VIEW_3D':
            cursor_location = area.spaces[0].cursor_location

    # Because vectors are pointers, we need to keep regenerating them
    cursorLocCopy = Vector((0.0, 0.0, 0.0))
    cursorLocCopy[0] = cursor_location[0]
    cursorLocCopy[1] = cursor_location[1]
    cursorLocCopy[2] = cursor_location[2]

    SwitchObjectMode(prevMode, target)

    # Restore the original cursor location and matrix
    bpy.data.scenes[bpy.context.scene.name].cursor_location = previous_cursor_loc

    return cursorLocCopy
