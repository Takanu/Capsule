import bpy, bmesh, time
from math import pi, radians, degrees
from mathutils import Vector

#//////////////////// - BASIC DEFINITIONS - ///////////////////////

def FocusObject(target):

    # If the target isnt visible, MAKE IT FUCKING VISIBLE.
    if target.hide is True:
        target.hide = False

    if target.hide_select is True:
        target.hide_select = False

    # If the mode is not object, we have to change it before using the
    # Select All command
    bpy.context.scene.objects.active = bpy.data.objects[target.name]

    prevMode = ''
    if target.mode != 'OBJECT':
        prevMode = target.mode
        bpy.context.scene.objects.active = bpy.data.objects[target.name]
        bpy.ops.object.mode_set(mode='OBJECT')

    #### Select and make target active
    bpy.ops.object.select_all(action='DESELECT')
    bpy.context.scene.objects.active = bpy.data.objects[target.name]
    bpy.ops.object.select_pattern(pattern=target.name)

    # Set the mode back
    if prevMode != '':
        bpy.ops.object.mode_set(mode=prevMode)

def SelectObject(target):

    # If the target isnt visible, MAKE IT FUCKING VISIBLE.
    if target.hide is True:
        target.hide = False

    if target.hide_select is True:
        target.hide_select = False

    target.select = True

def ActivateObject(target):

    # If the target isnt visible, MAKE IT FUCKING VISIBLE.
    if target.hide is True:
        target.hide = False

    if target.hide_select is True:
        target.hide_select = False

    bpy.context.scene.objects.active = bpy.data.objects[target.name]

def DuplicateObject(target):

    #### Select and make target active
    bpy.ops.object.select_all(action='DESELECT')
    bpy.context.scene.objects.active = bpy.data.objects[target.name]
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

    #### Select and make target active
    bpy.ops.object.select_all(action='DESELECT')

    for target in targets:
        bpy.context.scene.objects.active = bpy.data.objects[target.name]
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
    # Switches the object mode if it is currently not equal to the
    # current object mode.
    bpy.context.scene.objects.active = bpy.data.objects[target.name]
    prevMode = target.mode
    if target.mode != newMode:
        bpy.context.scene.objects.active = bpy.data.objects[target.name]
        bpy.ops.object.mode_set(mode=newMode)
        return prevMode

def MoveObject(target, context, location):
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

def CheckSuffix(string, suffix):

    strLength = len(string)
    suffixLength = len(suffix)
    diff = strLength - suffixLength
    index = string.rfind(suffix)

    #print("String Length...", strLength)
    #print("Suffix Length...", suffixLength)
    #print("Diff............", diff)
    #print("Index...........", index)

    if index == diff and index != -1:
        #print("Suffix is True")
        return True

    else:
        #print("Suffix is False")
        return False

def CheckPrefix(string, prefix):

    strLength = len(string)
    prefixLength = len(prefix)
    index = string.find(prefix)

    print("String..........", string)
    print("Prefix..........", prefix)
    print("String Length...", strLength)
    print("Prefix Length...", prefixLength)
    print("Index...........", index)

    if index == 0:
        print("Suffix is True")
        return True

    else:
        print("Suffix is False")
        return False



def CheckForTags(context, string):

    scn = context.scene.CAPScn
    user_preferences = context.user_preferences
    addon_prefs = user_preferences.addons[__package__].preferences

    hasLP = CheckSuffix(string, addon_prefs.lp_tag)
    hasHP = CheckSuffix(string, addon_prefs.hp_tag)
    hasCG = CheckSuffix(string, addon_prefs.cg_tag)
    hasCX = CheckSuffix(string, addon_prefs.cx_tag)

    if hasLP is False and hasHP is False and hasCG is False and hasCX is False:
        return False

    else:
        return True

def RemoveObjectTag(context, object, export_default):

    scn = context.scene.CAPScn

    print(">>> Removing Tags <<<")

    # Create a new string to return
    newString = ""

    for tag in export_default.tags:
        #print("Found tag...", tag.name)
        passed_type_filter = False

        #If the object matches the type filter, we can continue
        #print("Checking Type Filter.....", tag.object_type)

        typeFilter = 'NONE'

        if tag.object_type == '1':
            typeFilter = 'NONE'
            #print("Object matches type filter")
            passed_type_filter = True

        elif tag.object_type == '2':
            typeFilter = 'MESH'
        elif tag.object_type == '3':
            typeFilter = 'CURVE'
        elif tag.object_type == '4':
            typeFilter = 'SURFACE'
        elif tag.object_type == '5':
            typeFilter = 'META'
        elif tag.object_type == '6':
            typeFilter = 'FONT'
        elif tag.object_type == '7':
            typeFilter = 'ARMATURE'
        elif tag.object_type == '8':
            typeFilter = 'LATTICE'
        elif tag.object_type == '9':
            typeFilter = 'EMPTY'
        elif tag.object_type == '10':
            typeFilter = 'CAMERA'
        elif tag.object_type == '11':
            typeFilter = 'LAMP'
        elif tag.object_type == '12':
            typeFilter = 'SPEAKER'

        #print("Type Filter Found...", typeFilter)

        if tag.object_type != '1':
            if object.type == typeFilter:
                #print("Object matches type filter")
                passed_type_filter = True

        if passed_type_filter is True:
            if tag.name_filter != "":
                if tag.name_filter_type is '1':
                    if CheckSuffix(object.name, tag.name_filter) is True:
                        newString = object.name.replace(tag.name_filter, "")
                        print("Tag removed, new name:", newString)
                        return newString

                elif tag.name_filter_type is '2':
                    if object.name.find(tag.name_filter) == 0:
                        newString = object.name.replace(tag.name_filter, "")
                        print("Tag removed, new name:", newString)
                        return newString

                elif tag.name_filter_type is '3':
                    if object.name.find(tag.name_filter) != -1:
                        newString = object.name.replace(tag.name_filter, "")
                        print("Tag removed, new name:", newString)
                        return newString

    print("Could not remove tag, none found.  Exiting...")
    return ""

def IdentifyObjectTag(context, object, export_default):

    scn = context.scene

    print(">>> Checking Name Filter <<<")

    i = 0

    # Now collect objects based on the filtering categories
    for tag in export_default.tags:
        #print("Found tag...", tag.name)

        # NAME CHECK!
        passed_name_filter = False
        passed_type_filter = False

        if tag.name_filter != "":
            if tag.name_filter_type is '1':
                if CheckSuffix(object.name, tag.name_filter) is True:
                    #print("Object matches name filter")
                    passed_name_filter = True

            elif tag.name_filter_type is '2':
                if object.name.find(tag.name_filter) == 0:
                    #print("Object matches name filter")
                    passed_name_filter = True

            elif tag.name_filter_type is '3':
                if object.name.find(tag.name_filter) != -1:
                    #print("Object matches name filter")
                    passed_name_filter = True

        else:
            #print("Object matches name filter")
            passed_name_filter = True

        #print("Checking Type Filter.....", tag.object_type)

        typeFilter = 'NONE'

        if tag.object_type == '1':
            typeFilter = 'NONE'
            #print("Object matches type filter")
            passed_type_filter = True

        elif tag.object_type == '2':
            typeFilter = 'MESH'
        elif tag.object_type == '3':
            typeFilter = 'CURVE'
        elif tag.object_type == '4':
            typeFilter = 'SURFACE'
        elif tag.object_type == '5':
            typeFilter = 'META'
        elif tag.object_type == '6':
            typeFilter = 'FONT'
        elif tag.object_type == '7':
            typeFilter = 'ARMATURE'
        elif tag.object_type == '8':
            typeFilter = 'LATTICE'
        elif tag.object_type == '9':
            typeFilter = 'EMPTY'
        elif tag.object_type == '10':
            typeFilter = 'CAMERA'
        elif tag.object_type == '11':
            typeFilter = 'LAMP'
        elif tag.object_type == '12':
            typeFilter = 'SPEAKER'

        #print("Type Filter Found...", typeFilter)

        if tag.object_type != '1':
            if object.type == typeFilter:
                print("Object matches type filter")
                passed_type_filter = True

        if passed_type_filter is True and passed_name_filter is True:
            print("Filter Found! ...", str(i))
            return i

        i += 1

    return -1

def CompareObjectWithTag(context, object, tag):
    scn = context.scene

    print(">>> Comparing Object With Tag <<<")

    # NAME CHECK!
    passed_name_filter = False
    passed_type_filter = False

    if tag.name_filter != "":
        if tag.name_filter_type is '1':
            if CheckSuffix(object.name, tag.name_filter) is True:
                #print("Object matches name filter")
                passed_name_filter = True

        elif tag.name_filter_type is '2':
            if object.name.find(tag.name_filter) == 0:
                #print("Object matches name filter")
                passed_name_filter = True

        elif tag.name_filter_type is '3':
            if object.name.find(tag.name_filter) != -1:
                #print("Object matches name filter")
                passed_name_filter = True

    else:
        #print("Object matches name filter")
        passed_name_filter = True

    #print("Checking Type Filter.....", tag.object_type)

    typeFilter = 'NONE'

    if tag.object_type == '1':
        typeFilter = 'NONE'
        #print("Object matches type filter")
        passed_type_filter = True

    elif tag.object_type == '2':
        typeFilter = 'MESH'
    elif tag.object_type == '3':
        typeFilter = 'CURVE'
    elif tag.object_type == '4':
        typeFilter = 'SURFACE'
    elif tag.object_type == '5':
        typeFilter = 'META'
    elif tag.object_type == '6':
        typeFilter = 'FONT'
    elif tag.object_type == '7':
        typeFilter = 'ARMATURE'
    elif tag.object_type == '8':
        typeFilter = 'LATTICE'
    elif tag.object_type == '9':
        typeFilter = 'EMPTY'
    elif tag.object_type == '10':
        typeFilter = 'CAMERA'
    elif tag.object_type == '11':
        typeFilter = 'LAMP'
    elif tag.object_type == '12':
        typeFilter = 'SPEAKER'

    #print("Type Filter Found...", typeFilter)

    if tag.object_type != '1':
        if object.type == typeFilter:
            #print("Object matches type filter")
            passed_type_filter = True

    if passed_type_filter is True and passed_name_filter is True:
        print("Object matches tag!")
        return True

    print("Object doesn't match tag...")
    return False

def FindObjectsWithName(context, object_name):
    objects_found = []

    for object in context.scene.objects:
        if object.name.find(object_name) != -1:
            objects_found.append(object)

    return objects_found

def FindObjectWithTag(context, object_name, tag):

    scn = context.scene

    print(">>> Checking Name Filter <<<")

    # First, we need to make the name of the object to search for
    search_name = ""
    search_object = None

    if tag.name_filter != "":
        if tag.name_filter_type is '1':
            search_name = object_name + tag.name_filter

        elif tag.name_filter_type is '2':
            search_name = tag.name_filter + object_name

        if bpy.data.objects.find(search_name) != -1:
            search_object = bpy.data.objects[search_name]
            #print("Found search object......", search_object.name)
            #print("Checking Type Filter.....", tag.object_type)

            typeFilter = 'NONE'

            if tag.object_type == '1':
                typeFilter = 'NONE'
                #print("Object matches type filter")
                return search_object

            elif tag.object_type == '2':
                typeFilter = 'MESH'
            elif tag.object_type == '3':
                typeFilter = 'CURVE'
            elif tag.object_type == '4':
                typeFilter = 'SURFACE'
            elif tag.object_type == '5':
                typeFilter = 'META'
            elif tag.object_type == '6':
                typeFilter = 'FONT'
            elif tag.object_type == '7':
                typeFilter = 'ARMATURE'
            elif tag.object_type == '8':
                typeFilter = 'LATTICE'
            elif tag.object_type == '9':
                typeFilter = 'EMPTY'
            elif tag.object_type == '10':
                typeFilter = 'CAMERA'
            elif tag.object_type == '11':
                typeFilter = 'LAMP'
            elif tag.object_type == '12':
                typeFilter = 'SPEAKER'

            #print("Type Filter Found...", typeFilter)

            if tag.object_type != '1':
                if search_object.type == typeFilter:
                    print("Object matches type filter")
                    return search_object

    print("Object doesn't match type filter")
    return None


def SearchModifiers(target, currentList):

    print(">>> Searching Modifiers <<<")
    print(target.name)

    object_list = []

    mod_types = {'ARRAY', 'BOOLEAN', 'MIRROR', 'SCREW', 'ARMATURE', 'CAST', 'CURVE', 'HOOK', 'LATTICE', 'MESH_DEFORM', 'SHRINKWRAP', 'SIMPLE_DEFORM', 'WARP', 'WAVE'}

    # This is used to define all modifiers that share the same object location property
    mod_normal_types = {'BOOLEAN', 'SCREW', 'ARMATURE', 'CAST', 'CURVE', 'HOOK', 'LATTICE', 'MESH_DEFORM'}

    #Finds all the components in the object through modifiers that use objects
    for modifier in target.modifiers:
        if modifier.type in mod_types:
            print("Modifier Found...", modifier)

            #Normal Object Types
            if modifier.type in mod_normal_types:
                if modifier.object is not None:
                    print("Object Found In", modifier.name, ":", modifier.object.name)

                    # Find out if this object matches others in the list before adding it.
                    if (modifier.object in currentList) == False:
                        print("Object successfully added.")
                        object_list.append(modifier.object)
                        currentList.append(modifier.object)

            #Array
            elif modifier.type == 'ARRAY':
                if modifier.start_cap is not None:
                    print("Object Found In", modifier.name, ":", modifier.start_cap.name)

                    if (modifier.start_cap in currentList) == False:
                        print("Object successfully added.")
                        object_list.append(modifier.start_cap)
                        currentList.append(modifier.start_cap)

            #Mirror
            elif modifier.type == 'MIRROR':
                if modifier.mirror_object is not None:
                    print("Object Found In", modifier.name, ":", modifier.mirror_object.name)

                    if (modifier.mirror_object in currentList) == False:
                        print("Object successfully added.")
                        object_list.append(modifier.mirror_object)
                        currentList.append(modifier.mirror_object)

            #Shrinkwrap
            elif modifier.type == 'SHRINKWRAP':
                if modifier.target is not None:
                    print("Object Found In", modifier.name, ":", modifier.target.name)

                    if (modifier.target in currentList) == False:
                        print("Object successfully added.")
                        object_list.append(modifier.target)
                        currentList.append(modifier.target)

            #Simple Deform
            elif modifier.type == 'SIMPLE_DEFORM':
                if modifier.origin is not None:
                    print("Object Found In", modifier.name, ":", modifier.origin.name)

                    if (modifier.origin in currentList) == False:
                        print("Object successfully added.")
                        object_list.append(modifier.origin)
                        currentList.append(modifier.origin)

            #Warp
            elif modifier.type == 'WARP':
                if modifier.object_from is not None:
                    print("Object Found In", modifier.name, ":", modifier.object_from.name)

                    if (modifier.object_from in currentList) == False:
                        print("Object successfully added.")
                        object_list.append(modifier.object_from)
                        currentList.append(modifier.object_from)

                if modifier.object_to is not None:
                    print("Object Found In", modifier.name, ":", modifier.object_to.name)

                    if (modifier.object_to in currentList) == False:
                        print("Object successfully added.")
                        object_list.append(modifier.object_to)
                        currentList.append(modifier.object_to)

            #Wave
            elif modifier.type == 'WAVE':
                if modifier.start_position_object is not None:
                    print("Object Found In", modifier.name, ":", modifier.start_position_object.name)

                    if (modifier.start_position_object in currentList) == False:
                        print("Object successfully added.")
                        object_list.append(modifier.start_position_object)
                        currentList.append(modifier.start_position_object)


    return object_list

def SearchConstraints(target, currentList):

    print(">>> Searching Constraints <<<")
    print(target.name)

    object_list = []

    con_types_target = {'COPY_LOCATION', 'COPY_ROTATION', 'COPY_SCALE', 'COPY_TRANSFORMS', 'LIMIT_DISTANCE', 'TRANSFORM', 'CLAMP_TO', 'DAMPED_TRACK', 'LOCKED_TRACK', 'STRETCH_TO', 'TRACK_TO', 'ACTION', 'FLOOR', 'FOLLOW_PATH', 'PIVOT', 'SHRINKWRAP'}

    con_types_alt = {'RAWR'}

    for constraint in target.constraints:
        #Normal Object Types
        if constraint.type in con_types_target:
            if constraint.target is not None:
                print("Object Found In", constraint.name, ":", constraint.target.name)

                if (constraint.target in currentList) == False:
                    print("Object successfully added.")
                    object_list.append(constraint.target)
                    currentList.append(constraint.target)

    return object_list

def GetDependencies(objectList):

    print(">>> Getting Dependencies <<<")

    totalFoundList = []
    totalFoundList += objectList

    print("objectList...", objectList)

    checkedList = []
    currentList = []
    currentList += objectList

    while len(currentList) != 0:
        item = currentList.pop()
        print("Checking new objects...", item.name)

        modifierOutput = SearchModifiers(item, totalFoundList)
        constraintOutput = SearchConstraints(item, totalFoundList)

        currentList += modifierOutput
        currentList += constraintOutput

        checkedList.append(item)
        totalFoundList.append(item)

        # Parents can affect the export indirectly, so it needs to be looked at.
        if item.parent != None:
            if (item.parent in totalFoundList) is False:
                print("Parent found in", item.name, ":", item.parent.name)
                currentList.append(item.parent)

    print("Total found objects...", len(checkedList))
    print(checkedList)

    return checkedList

# Should help me avoid the bus issue.
def AddParent(child, parent):

    # I now have to add the cursor stuff here too, just in case...
    cursor_loc = bpy.data.scenes[bpy.context.scene.name].cursor_location
    previous_cursor_loc = [cursor_loc[0], cursor_loc[1], cursor_loc[2]]
    FocusObject(child)
    bpy.ops.view3D.snap_cursor_to_selected()

    bpy.ops.object.select_all(action='DESELECT')

    SelectObject(parent)
    SelectObject(child)

    bpy.context.scene.objects.active = parent

    bpy.ops.object.parent_set()

    # Now move the object
    FocusObject(child)
    bpy.ops.view3D.snap_selected_to_cursor()
    bpy.data.scenes[bpy.context.scene.name].cursor_location = previous_cursor_loc

def ClearParent(child):
    # Prepare the 3D cursor so it can keep the object in it's current location
    # After it stops being a component
    cursor_loc = bpy.data.scenes[bpy.context.scene.name].cursor_location
    previous_cursor_loc = [cursor_loc[0], cursor_loc[1], cursor_loc[2]]

    # Save the transform matrix before de-parenting
    matrixcopy = child.matrix_world.copy()

    # Move the cursor to the selected object
    FocusObject(child)
    bpy.ops.view3D.snap_cursor_to_selected()

    # Clear the parent
    bpy.ops.object.select_all(action='DESELECT')
    SelectObject(child)
    bpy.ops.object.parent_clear()

    # Now move the object
    bpy.ops.view3D.snap_selected_to_cursor()

    # Restore the original cursor location and matrix
    bpy.data.scenes[bpy.context.scene.name].cursor_location = previous_cursor_loc
    child.matrix_world = matrixcopy

def FindWorldSpaceObjectLocation(target, context):

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

def GetSceneGroups(scene, hasObjects):
    groups = []

    for item in scene.objects:
        for group in item.users_group:
            groupAdded = False

            for found_group in groups:
                if found_group.name == group.name:
                    groupAdded = True

            if hasObjects is False or len(group.objects) > 0:
                if groupAdded == False:
                    groups.append(group)

    return groups
