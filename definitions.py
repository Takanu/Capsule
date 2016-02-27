import bpy, bmesh, time
from math import *
from mathutils import Vector

#//////////////////// - BASIC DEFINITIONS - ///////////////////////

def FocusObject(target):

    # If the target isnt visible, MAKE IT FUCKING VISIBLE.
    if target.hide is True:
        target.hide = False

    if target.hide_select is True:
        target.hide_select = False

    #### Select and make target active
    bpy.ops.object.select_all(action='DESELECT')
    bpy.context.scene.objects.active = bpy.data.objects[target.name]
    bpy.ops.object.select_pattern(pattern=target.name)

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

def MoveObject(target, context, location):
	# This doesnt need the cursor, and will ensure nothing is animated
	# in the process

    print(">>> Moving Object <<<")

    # Prevent auto keyframing from being active
    autoKey = context.scene.tool_settings.use_keyframe_insert_auto
    lockTransform = target.lock_location

    context.scene.tool_settings.use_keyframe_insert_auto = False
    target.lock_location = (False, False, False)

    # This line is actually super-important, not sure why though...
    # FocusObject should fill the role of deselection...
    bpy.ops.object.select_all(action='DESELECT')

    # Move the object
    FocusObject(target)
    target.location = location

    # Preserving the objects location has to happen again, e_e
    #cursor_loc = bpy.data.scenes[bpy.context.scene.name].cursor_location
    #previous_cursor_loc = [cursor_loc[0], cursor_loc[1], cursor_loc[2]]

    # Move the cursor to the location
    #bpy.data.scenes[bpy.context.scene.name].cursor_location = location

    # Focus the object
    #FocusObject(target)

    # SNAP IT
    #bpy.ops.view3D.snap_selected_to_cursor()

    print("Object", target.name, "moved.... ", target.location)

    # Restore the location
    #bpy.data.scenes[bpy.context.scene.name].cursor_location = previous_cursor_loc

    # Restore the previous setting
    context.scene.tool_settings.use_keyframe_insert_auto = autoKey
    target.lock_location = lockTransform


def MoveObjects(targetLead, targets, context, location):
	# This doesnt need the cursor, and will ensure nothing is animated
	# in the process

    print(">>>> Moving Objects <<<<")

    # Prevent auto keyframing and location lock from being active
    autoKey = context.scene.tool_settings.use_keyframe_insert_auto
    lockTransform = targetLead.lock_location

    context.scene.tool_settings.use_keyframe_insert_auto = False
    targetLead.lock_location = (False, False, False)

    # Calculate the movement difference
    locationDiff = Vector((0.0, 0.0, 0.0))
    locationVec = Vector(location)
    locationDiff = locationVec - targetLead.location

    targetsToRemove = []

    # Check if any targets are children of any other object
    for child in targetLead.children:
        print("Checking TargetLead for Children...")
        for target in targets:
            if child.name == target.name:
                print("Removing Target", target.name)
                targetsToRemove.append(target)

    for target in targets:
        print("Checking Targets for Children...")
        for child in target.children:
            print("Found Child ", child.name)
            for otherTarget in targets:
                if child.name == otherTarget.name:
                    print("Removing Target", child.name)
                    targetsToRemove.append(child)

    for target in targetsToRemove:
        targets.remove(target)

    print("Child Check Complete.")

    bpy.ops.object.select_all(action='DESELECT')

    # Move the first object
    FocusObject(targetLead)
    targetLead.location = location

    print("Root Object", targetLead.name, "Moved... ", targetLead.location)
    print("Moving Secondary Objects...")

    # Move every other object by the differential
    bpy.ops.object.select_all(action='DESELECT')
    for object in targets:
        lockTransformSel = object.lock_location
        object.lock_location = (False, False, False)

        FocusObject(object)
        bpy.ops.transform.translate(value=locationDiff)

        print("Object", object.name, "moved.... ", object.location)

        object.lock_location = lockTransformSel


    # Restore the previous setting
    context.scene.tool_settings.use_keyframe_insert_auto = autoKey
    targetLead.lock_location = lockTransform

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

    scn = context.scene.GXScn
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

    scn = context.scene.GXScn

    print(">>> Removing Tags <<<")

    # Create a new string to return
    newString = ""

    for tag in export_default.tags:
        print("Found tag...", tag.name)
        passed_type_filter = False

        #If the object matches the type filter, we can continue
        print("Checking Type Filter.....", tag.object_type)

        typeFilter = 'NONE'

        if tag.object_type == '1':
            typeFilter = 'NONE'
            print("Object matches type filter")
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

        print("Type Filter Found...", typeFilter)

        if tag.object_type != '1':
            if object.type == typeFilter:
                print("Object matches type filter")
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
        print("Found tag...", tag.name)

        # NAME CHECK!
        passed_name_filter = False
        passed_type_filter = False

        if tag.name_filter != "":
            if tag.name_filter_type is '1':
                if CheckSuffix(object.name, tag.name_filter) is True:
                    print("Object matches name filter")
                    passed_name_filter = True

            elif tag.name_filter_type is '2':
                if object.name.find(tag.name_filter) == 0:
                    print("Object matches name filter")
                    passed_name_filter = True

            elif tag.name_filter_type is '3':
                if object.name.find(tag.name_filter) != -1:
                    print("Object matches name filter")
                    passed_name_filter = True

        else:
            print("Object matches name filter")
            passed_name_filter = True

        print("Checking Type Filter.....", tag.object_type)

        typeFilter = 'NONE'

        if tag.object_type == '1':
            typeFilter = 'NONE'
            print("Object matches type filter")
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

        print("Type Filter Found...", typeFilter)

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
                print("Object matches name filter")
                passed_name_filter = True

        elif tag.name_filter_type is '2':
            if object.name.find(tag.name_filter) == 0:
                print("Object matches name filter")
                passed_name_filter = True

        elif tag.name_filter_type is '3':
            if object.name.find(tag.name_filter) != -1:
                print("Object matches name filter")
                passed_name_filter = True

    else:
        print("Object matches name filter")
        passed_name_filter = True

    print("Checking Type Filter.....", tag.object_type)

    typeFilter = 'NONE'

    if tag.object_type == '1':
        typeFilter = 'NONE'
        print("Object matches type filter")
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

    print("Type Filter Found...", typeFilter)

    if tag.object_type != '1':
        if object.type == typeFilter:
            print("Object matches type filter")
            passed_type_filter = True

    if passed_type_filter is True and passed_name_filter is True:
        print("Object matches tag!")
        return True

    print("Object doesn't match tag...")
    return False

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
            print("Found search object......", search_object.name)
            print("Checking Type Filter.....", tag.object_type)

            typeFilter = 'NONE'

            if tag.object_type == '1':
                typeFilter = 'NONE'
                print("Object matches type filter")
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

            print("Type Filter Found...", typeFilter)

            if tag.object_type != '1':
                if search_object.type == typeFilter:
                    print("Object matches type filter")
                    return search_object

    return None
