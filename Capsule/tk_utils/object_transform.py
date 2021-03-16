
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
    auto_key = context.scene.tool_settings.use_keyframe_insert_auto
    lock_transform = target.lock_location

    context.scene.tool_settings.use_keyframe_insert_auto = False
    target.lock_location = (False, False, False)

    # Save the current cursor location
    cursor_loc = bpy.data.scenes[bpy.context.scene.name].cursor.location
    previous_cursor_loc = [cursor_loc[0], cursor_loc[1], cursor_loc[2]]

    # This line is actually super-important, not sure why though...
    # FocusObject should fill the role of deselection...
    bpy.ops.object.select_all(action='DESELECT')

    # Calculate the translation vector using the 3D cursor
    FocusObject(target)
    bpy.ops.view3d.snap_cursor_to_selected()
    translation_loc = Vector((0.0, 0.0, 0.0))

    # 2.79 Code
    # for area in context.screen.areas:
    #     if area.type == 'VIEW_3D':
    #         translation_loc = area.spaces[0].cursor.location

    translation_loc = bpy.context.scene.cursor.location

    # Calculate the movement difference
    locationDiff = copyLocation - translation_loc

    bpy.ops.transform.translate(
        value=locationDiff,
        constraint_axis=(False, False, False),
        orient_type='GLOBAL',
        mirror=False,
        use_proportional_edit=False,
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
    bpy.data.scenes[bpy.context.scene.name].cursor.location = previous_cursor_loc

    # Restore the previous setting
    context.scene.tool_settings.use_keyframe_insert_auto = auto_key
    target.lock_location = lock_transform

def MoveObjectFailsafe(target, context, location, region):
    """
    Safely moves the given object to the given location.  Will ensure nothing is animated or screwed up in the process.
    WORKAROUND FOR BLENDER 2.8 CRASH FUNTIMES.
    """

	# This doesnt need the cursor, and will ensure nothing is animated
	# in the process

    print(">>>>>> Moving Object <<<<<<")

    copyLocation = Vector((location[0], location[1], location[2]))

    # Prevent auto keyframing from being active
    auto_key = context.scene.tool_settings.use_keyframe_insert_auto
    lock_transform = target.lock_location

    context.scene.tool_settings.use_keyframe_insert_auto = False
    target.lock_location = (False, False, False)

    # Save the current cursor location
    cursor_loc = bpy.data.scenes[bpy.context.scene.name].cursor.location
    previous_cursor_loc = [cursor_loc[0], cursor_loc[1], cursor_loc[2]]

    # This line is actually super-important, not sure why though...
    # FocusObject should fill the role of deselection...
    bpy.ops.object.select_all(action='DESELECT')

    # Calculate the translation vector using the 3D cursor
    FocusObject(target)
    bpy.ops.view3d.snap_cursor_to_selected()
    translation_loc = Vector((0.0, 0.0, 0.0))

    translation_loc = bpy.context.scene.cursor.location

    previous_mode = bpy.context.active_object.mode
    override = {'region': region}

    # Calculate the movement difference
    locationDiff = copyLocation - translation_loc

    # NEW Translate
    bpy.ops.transform.translate(
        override,
        value = locationDiff,
        constraint_axis = (False, False, False),
        orient_type = 'GLOBAL',
        mirror = False,
        use_proportional_edit = False,
        snap = False,
        release_confirm = False,
    )

    bpy.ops.object.mode_set(mode=previous_mode)

    # Position the cursor back to it's original location
    bpy.data.scenes[bpy.context.scene.name].cursor.location = previous_cursor_loc

    # Restore the previous setting
    context.scene.tool_settings.use_keyframe_insert_auto = auto_key
    target.lock_location = lock_transform

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
    auto_key = context.scene.tool_settings.use_keyframe_insert_auto
    lock_transform = target.lock_location

    context.scene.tool_settings.use_keyframe_insert_auto = False
    target.lock_location = (False, False, False)

    # Save the current cursor location
    cursor_loc = bpy.data.scenes[bpy.context.scene.name].cursor.location
    previous_cursor_loc = [cursor_loc[0], cursor_loc[1], cursor_loc[2]]

    # This line is actually super-important, not sure why though...
    # FocusObject should fill the role of deselection...
    bpy.ops.object.select_all(action='DESELECT')

    # Calculate the translation vector using the 3D cursor
    prevMode = SwitchObjectMode('POSE', target)
    bpy.data.objects[target.name].data.bones.active = bpy.data.objects[target.name].pose.bones[bone.name].bone
    bpy.ops.view3d.snap_cursor_to_selected()
    translation_loc = Vector((0.0, 0.0, 0.0))

    #print("RAWR")
    translation_loc = bpy.context.scene.cursor.location

    # for area in context.screen.areas:
    #     if area.type == 'VIEW_3D':
    #         translation_loc = area.spaces[0].cursor.location

    #print(translation_loc)

    # Calculate the movement difference
    locationDiff = copyLocation - cursor.location

    bpy.ops.transform.translate(
        value=locationDiff,
        constraint_axis=(False, False, False),
        orient_type='GLOBAL',
        mirror=False,
        use_proportional_edit='DISABLED',
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
    #bpy.data.scenes[bpy.context.scene.name].cursor.location = previous_cursor_loc

    # Restore the previous setting
    #context.scene.tool_settings.use_keyframe_insert_auto = auto_key
    #target.lock_location = lock_transform

def MoveObjects(targetLead, targets, context, location):
    """
    Safely moves the given objects to the given location.  Will ensure nothing is animated or screwed up in the process.
    """

	# This doesnt need the cursor, and will ensure nothing is animated
	# in the process

    copyLocation = Vector((location[0], location[1], location[2]))

    # Prevent auto keyframing and location lock from being active
    auto_key = context.scene.tool_settings.use_keyframe_insert_auto
    lock_transform = targetLead.lock_location

    context.scene.tool_settings.use_keyframe_insert_auto = False
    targetLead.lock_location = (False, False, False)

    # Save the current cursor location
    cursor_loc = bpy.data.scenes[bpy.context.scene.name].cursor.location
    previous_cursor_loc = [cursor_loc[0], cursor_loc[1], cursor_loc[2]]

    # Calculate the translation vector using the 3D cursor
    bpy.ops.object.select_all(action='DESELECT')
    FocusObject(targetLead)
    bpy.ops.view3d.snap_cursor_to_selected()
    root_location = Vector((0.0, 0.0, 0.0))

    root_location = bpy.context.scene.cursor.location

    # for area in context.screen.areas:
    #     if area.type == 'VIEW_3D':
    #         root_location = area.spaces[0].cursor.location

    # Calculate the movement difference
    locationDiff = copyLocation - root_location

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
        orient_type='GLOBAL',
        mirror=False,
        use_proportional_edit='DISABLED',
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
    bpy.data.scenes[bpy.context.scene.name].cursor.location = previous_cursor_loc

    # Restore the previous setting
    context.scene.tool_settings.use_keyframe_insert_auto = auto_key
    targetLead.lock_location = lock_transform

def RotateObjectSafe(target, context, rotation, forward):
    """
    Safely rotates the given objects with the given rotation.  Will ensure nothing is animated or screwed up in the process.
    """

    # Prevent auto keyframing and location lock from being active
    auto_key = context.scene.tool_settings.use_keyframe_insert_auto
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
                orient_type='GLOBAL',
                release_confirm=True
                )

    # Restore the pivot
    for area in context.screen.areas:
        if area.type == 'VIEW_3D':
            area.spaces[0].pivot_point = backupPivot
            area.spaces[0].use_pivot_point_align = backupAlign

    # Restore the previous setting
    context.scene.tool_settings.use_keyframe_insert_auto = auto_key

def MoveAll(target, context, location):
    """
    ???
    """
    # This doesnt need the cursor, and will ensure nothing is animated
	# in the process

    print('Moving all objects...')

    copyLocation = [0.0, 0.0, 0.0]
    copyLocation[0] = location[0]
    copyLocation[1] = location[1]
    copyLocation[2] = location[2]

    # Prevent auto keyframing and location lock from being active
    auto_key = context.scene.tool_settings.use_keyframe_insert_auto
    lock_transform = target.lock_location

    context.scene.tool_settings.use_keyframe_insert_auto = False
    target.lock_location = (False, False, False)

    # Save the current cursor location
    cursor_loc = bpy.data.scenes[context.scene.name].cursor.location
    previous_cursor_loc = [cursor_loc[0], cursor_loc[1], cursor_loc[2]]

    # Calculate the translation vector using the 3D cursor
    bpy.ops.object.select_all(action='DESELECT')
    FocusObject(target)
    bpy.ops.view3d.snap_cursor_to_selected()
    root_location = (0.0, 0.0, 0.0)

    print('Getting cursor...')

    root_location = context.scene.cursor.location

    print('Did it break?  aaaaaaaa')

    # for area in context.screen.areas:
    #     if area.type == 'VIEW_3D':
    #         print(area.spaces[0].cursor.location)
    #         root_location = area.spaces[0].cursor.location

    # Calculate the movement difference
    locationDiff = []
    locationDiff.append(copyLocation[0] - root_location[0])
    locationDiff.append(copyLocation[1] - root_location[1])
    locationDiff.append(copyLocation[2] - root_location[2])

    bpy.ops.object.select_all(action='SELECT')
    ActivateObject(target)

    previous_mode = bpy.context.active_object.mode

    print('ok now moving for realsies - ', locationDiff)

    # 2.79 translate
    bpy.ops.transform.translate(
        value = locationDiff,
        constraint_axis = (False, False, False),
        orient_type = 'GLOBAL',
        mirror = False,
        use_proportional_edit = False,
        snap = False,
        release_confirm = False,
    )
    
    print('All objects moved, resetting cursor...')

    bpy.ops.object.mode_set(mode=previous_mode)

    # Position the cursor back to it's original location
    bpy.data.scenes[bpy.context.scene.name].cursor.location = previous_cursor_loc

    # Restore the previous setting
    context.scene.tool_settings.use_keyframe_insert_auto = auto_key
    target.lock_location = lock_transform

    print('Move finished.')

def MoveAllFailsafe(context, target, destination, region):
    """
    Moves every object in the scene safely
    BLENDER 2.8 - This also uses a region to ensure that it moves in a 3D View region that hasnt been deallocated.
    """
    # This doesnt need the cursor, and will ensure nothing is animated
	# in the process

    print('MOVEMENT TEST')

    target_location = [0.0, 0.0, 0.0]
    target_location[0] = destination[0]
    target_location[1] = destination[1]
    target_location[2] = destination[2]

    # Prevent auto keyframing and location lock from being active
    auto_key = context.scene.tool_settings.use_keyframe_insert_auto
    lock_transform = target.lock_location

    context.scene.tool_settings.use_keyframe_insert_auto = False
    target.lock_location = (False, False, False)

    # Save the current cursor location
    cursor_loc = bpy.data.scenes[context.scene.name].cursor.location
    previous_cursor_loc = [cursor_loc[0], cursor_loc[1], cursor_loc[2]]

    # Calculate the translation vector using the 3D cursor
    bpy.ops.object.select_all(action='DESELECT')
    FocusObject(target)
    bpy.ops.view3d.snap_cursor_to_selected()
    root_location = (0.0, 0.0, 0.0)

    print('Getting cursor...')

    root_location = context.scene.cursor.location

    print('Did it break?  aaaaaaaa')

    # for area in context.screen.areas:
    #     if area.type == 'VIEW_3D':
    #         print(area.spaces[0].cursor.location)
    #         root_location = area.spaces[0].cursor.location

    # Calculate the movement difference
    locationDiff = []
    locationDiff.append(target_location[0] - root_location[0])
    locationDiff.append(target_location[1] - root_location[1])
    locationDiff.append(target_location[2] - root_location[2])

    bpy.ops.object.select_all(action='SELECT')
    ActivateObject(target)

    previous_mode = bpy.context.active_object.mode

    print('ok now moving for realsies - ', locationDiff)

    override = {'region': region}

    # NEW Translate
    bpy.ops.transform.translate(
        override,
        value = locationDiff,
        constraint_axis = (False, False, False),
        orient_type = 'GLOBAL',
        mirror = False,
        use_proportional_edit = False,
        snap = False,
        release_confirm = False,
    )
    
    print('All objects moved, resetting cursor...')

    bpy.ops.object.mode_set(mode=previous_mode)

    # Position the cursor back to it's original location
    bpy.data.scenes[bpy.context.scene.name].cursor.location = previous_cursor_loc

    # Restore the previous setting
    context.scene.tool_settings.use_keyframe_insert_auto = auto_key
    target.lock_location = lock_transform

    print('Move finished.')

def RotateAll(target, context, rotation, constraintAxis):
    """
    ???
    """
    # Prevent auto keyframing and location lock from being active
    auto_key = context.scene.tool_settings.use_keyframe_insert_auto
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
        orient_type='GLOBAL',
        release_confirm=True
        )

    # Restore the pivot
    for area in context.screen.areas:
        if area.type == 'VIEW_3D':
            area.spaces[0].pivot_point = backupPivot
            area.spaces[0].use_pivot_point_align = backupAlign

    # Restore the previous setting
    context.scene.tool_settings.use_keyframe_insert_auto = auto_key

def RotateAllSafe(target, context, rotation, forward):
    """
    ???
    """

    # Prevent auto keyframing and location lock from being active
    auto_key = context.scene.tool_settings.use_keyframe_insert_auto
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
                orient_type='GLOBAL',
                release_confirm=True
                )

    # Restore the pivot
    for area in context.screen.areas:
        if area.type == 'VIEW_3D':
            area.spaces[0].pivot_point = backupPivot
            area.spaces[0].use_pivot_point_align = backupAlign

    # Restore the previous setting
    context.scene.tool_settings.use_keyframe_insert_auto = auto_key

def ScaleAll(context, scale, constraintAxis):
    """
    ???
    """
    # Prevent auto keyframing and location lock from being active
    auto_key = context.scene.tool_settings.use_keyframe_insert_auto
    context.scene.tool_settings.use_keyframe_insert_auto = False

    bpy.ops.object.select_all(action='SELECT')

    bpy.ops.transform.resize(
        value=scale,
        constraint_axis=constraintAxis,
        orient_type='GLOBAL',
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
    context.scene.tool_settings.use_keyframe_insert_auto = auto_key