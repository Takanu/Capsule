
import bpy
from mathutils import Vector
from .object_ops import SwitchObjectMode
from .select import FocusObject, SelectObject, ActivateObject

def MoveObject(target, context, location):
    """
    Safely moves the given object to the given location.  Will ensure nothing is animated or screwed up in the process.
    """

	# This doesnt need the cursor, and will ensure nothing is animated
	# in the process

    print(">>>>>> Moving Object <<<<<<")

    copyLocation = Vector((location[0], location[1], location[2]))

    # Prevent auto keyframing from being active
    autoKey = context.scene.tool_settings.use_keyframe_insert_auto
    lockTransform = target.lock_location

    context.scene.tool_settings.use_keyframe_insert_auto = False
    target.lock_location = (False, False, False)

    # Save the current cursor location
    cursor_loc = bpy.data.scenes[bpy.context.scene.name].cursor_location
    previous_cursor_loc = [cursor_loc[0], cursor_loc[1], cursor_loc[2]]

    # This line is actually super-important, not sure why though...
    # FocusObject should fill the role of deselection...
    bpy.ops.object.select_all(action='DESELECT')

    # Calculate the translation vector using the 3D cursor
    FocusObject(target)
    bpy.ops.view3d.snap_cursor_to_selected()
    cursor_location = Vector((0.0, 0.0, 0.0))

    for area in context.screen.areas:
        if area.type == 'VIEW_3D':
            cursor_location = area.spaces[0].cursor_location

    # Calculate the movement difference
    locationDiff = copyLocation - cursor_location

    bpy.ops.transform.translate(
        value=locationDiff,
        constraint_axis=(False, False, False),
        constraint_orientation='GLOBAL',
        mirror=False,
        proportional='DISABLED',
        proportional_edit_falloff='SMOOTH',
        proportional_size=1.0,
        snap=False,
        snap_target='CLOSEST',
        snap_point=(0.0, 0.0, 0.0),
        snap_align=False,
        snap_normal=(0.0, 0.0, 0.0),
        gpencil_strokes=False,
        texture_space=False,
        remove_on_cancel=False,
        release_confirm=False)

    # Position the cursor back to it's original location
    bpy.data.scenes[bpy.context.scene.name].cursor_location = previous_cursor_loc

    # Restore the previous setting
    context.scene.tool_settings.use_keyframe_insert_auto = autoKey
    target.lock_location = lockTransform

def MoveBone(target, bone, context, location):
    """
    Safely moves the given bone to the given location.  Will ensure nothing is animated or screwed up in the process.
    """

	# This doesnt need the cursor, and will ensure nothing is animated
	# in the process

    #print(">>> Moving Object <<<")

    copyLocation = Vector((0.0, 0.0, 0.0))
    copyLocation[0] = location[0]
    copyLocation[1] = location[1]
    copyLocation[2] = location[2]

    # Prevent auto keyframing from being active
    autoKey = context.scene.tool_settings.use_keyframe_insert_auto
    lockTransform = target.lock_location

    context.scene.tool_settings.use_keyframe_insert_auto = False
    target.lock_location = (False, False, False)

    # Save the current cursor location
    cursor_loc = bpy.data.scenes[bpy.context.scene.name].cursor_location
    previous_cursor_loc = [cursor_loc[0], cursor_loc[1], cursor_loc[2]]

    # This line is actually super-important, not sure why though...
    # FocusObject should fill the role of deselection...
    bpy.ops.object.select_all(action='DESELECT')

    # Calculate the translation vector using the 3D cursor
    prevMode = SwitchObjectMode('POSE', target)
    bpy.data.objects[target.name].data.bones.active = bpy.data.objects[target.name].pose.bones[bone.name].bone
    bpy.ops.view3d.snap_cursor_to_selected()
    cursor_location = Vector((0.0, 0.0, 0.0))

    #print("RAWR")

    for area in context.screen.areas:
        if area.type == 'VIEW_3D':
            cursor_location = area.spaces[0].cursor_location

    #print(cursor_location)

    # Calculate the movement difference
    locationDiff = copyLocation - cursor_location

    bpy.ops.transform.translate(
        value=locationDiff,
        constraint_axis=(False, False, False),
        constraint_orientation='GLOBAL',
        mirror=False,
        proportional='DISABLED',
        proportional_edit_falloff='SMOOTH',
        proportional_size=1.0,
        snap=False,
        snap_target='CLOSEST',
        snap_point=(0.0, 0.0, 0.0),
        snap_align=False,
        snap_normal=(0.0, 0.0, 0.0),
        gpencil_strokes=False,
        texture_space=False,
        remove_on_cancel=False,
        release_confirm=False)

    #print("Object", bone.name, "moved.... ", bone.location)

    SwitchObjectMode(prevMode, target)

    # Position the cursor back to it's original location
    #bpy.data.scenes[bpy.context.scene.name].cursor_location = previous_cursor_loc

    # Restore the previous setting
    #context.scene.tool_settings.use_keyframe_insert_auto = autoKey
    #target.lock_location = lockTransform

def MoveObjects(targetLead, targets, context, location):
    """
    Safely moves the given objects to the given location.  Will ensure nothing is animated or screwed up in the process.
    """

	# This doesnt need the cursor, and will ensure nothing is animated
	# in the process

    copyLocation = Vector((location[0], location[1], location[2]))

    # Prevent auto keyframing and location lock from being active
    autoKey = context.scene.tool_settings.use_keyframe_insert_auto
    lockTransform = targetLead.lock_location

    context.scene.tool_settings.use_keyframe_insert_auto = False
    targetLead.lock_location = (False, False, False)

    # Save the current cursor location
    cursor_loc = bpy.data.scenes[bpy.context.scene.name].cursor_location
    previous_cursor_loc = [cursor_loc[0], cursor_loc[1], cursor_loc[2]]

    # Calculate the translation vector using the 3D cursor
    bpy.ops.object.select_all(action='DESELECT')
    FocusObject(targetLead)
    bpy.ops.view3d.snap_cursor_to_selected()
    rootLocation = Vector((0.0, 0.0, 0.0))

    for area in context.screen.areas:
        if area.type == 'VIEW_3D':
            rootLocation = area.spaces[0].cursor_location

    # Calculate the movement difference
    locationDiff = copyLocation - rootLocation

    targetsToRemove = []

    # Check if any targets are children of any other object
    for child in targetLead.children:
        print("Checking TargetLead for Children...")
        for target in targets:
            if child.name == target.name:
                print("Removing Target", target.name)
                targetsToRemove.append(target)

    for target in targets:
        print("Checking Targets for Children...", target.name)
        for child in target.children:
            print("Found Child ", child.name)
            for otherTarget in targets:
                if child.name == otherTarget.name:
                    print("Removing Target", child.name)
                    targetsToRemove.append(child)

    for target in targetsToRemove:
        if target in targets:
            targets.remove(target)

    bpy.ops.object.select_all(action='DESELECT')

    # Lets try moving all the fucking objects this time
    FocusObject(targetLead)

    for item in targets:
        SelectObject(item)

    bpy.ops.transform.translate(
        value=locationDiff,
        constraint_axis=(False, False, False),
        constraint_orientation='GLOBAL',
        mirror=False,
        proportional='DISABLED',
        proportional_edit_falloff='SMOOTH',
        proportional_size=1.0,
        snap=False,
        snap_target='CLOSEST',
        snap_point=(0.0, 0.0, 0.0),
        snap_align=False,
        snap_normal=(0.0, 0.0, 0.0),
        gpencil_strokes=False,
        texture_space=False,
        remove_on_cancel=False,
        release_confirm=False)

    # Position the cursor back to it's original location
    bpy.data.scenes[bpy.context.scene.name].cursor_location = previous_cursor_loc

    # Restore the previous setting
    context.scene.tool_settings.use_keyframe_insert_auto = autoKey
    targetLead.lock_location = lockTransform

def RotateObjectSafe(target, context, rotation, forward):
    """
    Safely rotates the given objects with the given rotation.  Will ensure nothing is animated or screwed up in the process.
    """

    # Prevent auto keyframing and location lock from being active
    autoKey = context.scene.tool_settings.use_keyframe_insert_auto
    context.scene.tool_settings.use_keyframe_insert_auto = False

    FocusObject(target)

    # Obtain the current rotation mode
    order = target.rotation_mode

    # Sort out how we're going to filter through the rotation order
    rotationOrder = []
    rotationComponents = []
    axisX = [0, (1.0, 0.0, 0.0), (True, False, False)]
    axisY = [1, (0.0, 1.0, 0.0), (False, True, False)]
    axisZ = [2, (0.0, 0.0, 1.0), (False, False, True)]

    if order == 'ZYX':
        if forward is True:
            rotationComponents = [axisZ, axisY, axisX]
        else:
            rotationComponents = [axisX, axisY, axisZ]
    elif order == 'ZXY':
        if forward is True:
            rotationComponents = [axisZ, axisX, axisY]
        else:
            rotationComponents = [axisY, axisX, axisZ]
    elif order == 'YZX':
        if forward is True:
            rotationComponents = [axisY, axisZ, axisX]
        else:
            rotationComponents = [axisX, axisZ, axisY]
    elif order == 'YXZ':
        if forward is True:
            rotationComponents = [axisY, axisX, axisZ]
        else:
            rotationComponents = [axisZ, axisX, axisY]
    elif order == 'XZY':
        if forward is True:
            rotationComponents = [axisX, axisZ, axisY]
        else:
            rotationComponents = [axisY, axisZ, axisX]
    elif order == 'XYZ':
        if forward is True:
            rotationComponents = [axisX, axisY, axisZ]
        else:
            rotationComponents = [axisZ, axisY, axisX]


    # Set the pivot to be the target object
    backupPivot = 'CURSOR'
    backupAlign = False
    for area in context.screen.areas:
        if area.type == 'VIEW_3D':
            backupPivot = area.spaces[0].pivot_point
            backupAlign = area.spaces[0].use_pivot_point_align
            area.spaces[0].pivot_point = 'ACTIVE_ELEMENT'
            area.spaces[0].use_pivot_point_align = False

    # Rotate in Euler order
    for i, item in enumerate(rotationComponents):
        if rotation[item[0]] != 1:

            bpy.ops.transform.rotate(
                value=rotation[item[0]],
                axis=item[1],
                constraint_axis=item[2],
                constraint_orientation='GLOBAL',
                release_confirm=True
                )

    # Restore the pivot
    for area in context.screen.areas:
        if area.type == 'VIEW_3D':
            area.spaces[0].pivot_point = backupPivot
            area.spaces[0].use_pivot_point_align = backupAlign

    # Restore the previous setting
    context.scene.tool_settings.use_keyframe_insert_auto = autoKey

def MoveAll(target, context, location):
    """
    ???
    """
    # This doesnt need the cursor, and will ensure nothing is animated
	# in the process

    copyLocation = Vector((0.0, 0.0, 0.0))
    copyLocation[0] = location[0]
    copyLocation[1] = location[1]
    copyLocation[2] = location[2]

    # Prevent auto keyframing and location lock from being active
    autoKey = context.scene.tool_settings.use_keyframe_insert_auto
    lockTransform = target.lock_location

    context.scene.tool_settings.use_keyframe_insert_auto = False
    target.lock_location = (False, False, False)

    # Save the current cursor location
    cursor_loc = bpy.data.scenes[bpy.context.scene.name].cursor_location
    previous_cursor_loc = [cursor_loc[0], cursor_loc[1], cursor_loc[2]]

    # Calculate the translation vector using the 3D cursor
    bpy.ops.object.select_all(action='DESELECT')
    FocusObject(target)
    bpy.ops.view3d.snap_cursor_to_selected()
    rootLocation = Vector((0.0, 0.0, 0.0))

    for area in context.screen.areas:
        if area.type == 'VIEW_3D':
            print(area.spaces[0].cursor_location)
            rootLocation = area.spaces[0].cursor_location

    # Calculate the movement difference
    locationDiff = copyLocation - rootLocation

    bpy.ops.object.select_all(action='SELECT')
    ActivateObject(target)

    bpy.ops.transform.translate(
        value=locationDiff,
        constraint_axis=(False, False, False),
        constraint_orientation='GLOBAL',
        mirror=False,
        proportional='DISABLED',
        proportional_edit_falloff='SMOOTH',
        proportional_size=1.0,
        snap=False,
        snap_target='CLOSEST',
        snap_point=(0.0, 0.0, 0.0),
        snap_align=False,
        snap_normal=(0.0, 0.0, 0.0),
        gpencil_strokes=False,
        texture_space=False,
        remove_on_cancel=False,
        release_confirm=False
        )

    # Position the cursor back to it's original location
    bpy.data.scenes[bpy.context.scene.name].cursor_location = previous_cursor_loc

    # Restore the previous setting
    context.scene.tool_settings.use_keyframe_insert_auto = autoKey
    target.lock_location = lockTransform

def RotateAll(target, context, rotation, constraintAxis):
    """
    ???
    """
    # Prevent auto keyframing and location lock from being active
    autoKey = context.scene.tool_settings.use_keyframe_insert_auto
    context.scene.tool_settings.use_keyframe_insert_auto = False

    bpy.ops.object.select_all(action='SELECT')
    ActivateObject(target)

    # Set the pivot to be the target object
    backupPivot = 'CURSOR'
    backupAlign = False
    for area in context.screen.areas:
        if area.type == 'VIEW_3D':
            backupPivot = area.spaces[0].pivot_point
            backupAlign = area.spaces[0].use_pivot_point_align
            area.spaces[0].pivot_point = 'ACTIVE_ELEMENT'
            area.spaces[0].use_pivot_point_align = False

    bpy.ops.transform.rotate(
        value=radians(rotation),
        axis=(1.0, 1.0, 1.0),
        constraint_axis=constraintAxis,
        constraint_orientation='GLOBAL',
        release_confirm=True
        )

    # Restore the pivot
    for area in context.screen.areas:
        if area.type == 'VIEW_3D':
            area.spaces[0].pivot_point = backupPivot
            area.spaces[0].use_pivot_point_align = backupAlign

    # Restore the previous setting
    context.scene.tool_settings.use_keyframe_insert_auto = autoKey

def RotateAllSafe(target, context, rotation, forward):
    """
    ???
    """

    # Prevent auto keyframing and location lock from being active
    autoKey = context.scene.tool_settings.use_keyframe_insert_auto
    context.scene.tool_settings.use_keyframe_insert_auto = False

    bpy.ops.object.select_all(action='SELECT')
    ActivateObject(target)

    # Obtain the current rotation mode
    order = target.rotation_mode

    # Sort out how we're going to filter through the rotation order
    rotationOrder = []
    rotationComponents = []
    axisX = [0, (1.0, 0.0, 0.0), (True, False, False)]
    axisY = [1, (0.0, 1.0, 0.0), (False, True, False)]
    axisZ = [2, (0.0, 0.0, 1.0), (False, False, True)]

    if order == 'ZYX':
        if forward is True:
            rotationComponents = [axisZ, axisY, axisX]
        else:
            rotationComponents = [axisX, axisY, axisZ]
    elif order == 'ZXY':
        if forward is True:
            rotationComponents = [axisZ, axisX, axisY]
        else:
            rotationComponents = [axisY, axisX, axisZ]
    elif order == 'YZX':
        if forward is True:
            rotationComponents = [axisY, axisZ, axisX]
        else:
            rotationComponents = [axisX, axisZ, axisY]
    elif order == 'YXZ':
        if forward is True:
            rotationComponents = [axisY, axisX, axisZ]
        else:
            rotationComponents = [axisZ, axisX, axisY]
    elif order == 'XZY':
        if forward is True:
            rotationComponents = [axisX, axisZ, axisY]
        else:
            rotationComponents = [axisY, axisZ, axisX]
    elif order == 'XYZ':
        if forward is True:
            rotationComponents = [axisX, axisY, axisZ]
        else:
            rotationComponents = [axisZ, axisY, axisX]


    # Set the pivot to be the target object
    backupPivot = 'CURSOR'
    backupAlign = False
    for area in context.screen.areas:
        if area.type == 'VIEW_3D':
            backupPivot = area.spaces[0].pivot_point
            backupAlign = area.spaces[0].use_pivot_point_align
            area.spaces[0].pivot_point = 'ACTIVE_ELEMENT'
            area.spaces[0].use_pivot_point_align = False

    # Rotate in Euler order
    for i, item in enumerate(rotationComponents):
        if rotation[item[0]] != 1:

            bpy.ops.transform.rotate(
                value=rotation[item[0]],
                axis=item[1],
                constraint_axis=item[2],
                constraint_orientation='GLOBAL',
                release_confirm=True
                )

    # Restore the pivot
    for area in context.screen.areas:
        if area.type == 'VIEW_3D':
            area.spaces[0].pivot_point = backupPivot
            area.spaces[0].use_pivot_point_align = backupAlign

    # Restore the previous setting
    context.scene.tool_settings.use_keyframe_insert_auto = autoKey

def ScaleAll(context, scale, constraintAxis):
    """
    ???
    """
    # Prevent auto keyframing and location lock from being active
    autoKey = context.scene.tool_settings.use_keyframe_insert_auto
    context.scene.tool_settings.use_keyframe_insert_auto = False

    bpy.ops.object.select_all(action='SELECT')

    bpy.ops.transform.resize(
        value=scale,
        constraint_axis=constraintAxis,
        constraint_orientation='GLOBAL',
        mirror=False,
        proportional='DISABLED',
        proportional_edit_falloff='SMOOTH',
        proportional_size=1.0,
        snap=False,
        snap_target='CLOSEST',
        snap_point=(0.0, 0.0, 0.0),
        snap_align=False,
        snap_normal=(0.0, 0.0, 0.0),
        gpencil_strokes=False,
        texture_space=False,
        remove_on_cancel=False,
        release_confirm=False
        )

    # Restore the previous setting
    context.scene.tool_settings.use_keyframe_insert_auto = autoKey