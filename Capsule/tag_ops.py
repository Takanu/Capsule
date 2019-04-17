
import bpy
from .tk_utils import text_ops

def CheckForTags(context, string):

    scn = context.scene.CAPScn
    preferences = context.preferences
    addon_prefs = preferences.addons[__package__].preferences

    hasLP = text_ops.CheckSuffix(string, addon_prefs.lp_tag)
    hasHP = text_ops.CheckSuffix(string, addon_prefs.hp_tag)
    hasCG = text_ops.CheckSuffix(string, addon_prefs.cg_tag)
    hasCX = text_ops.CheckSuffix(string, addon_prefs.cx_tag)

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
            typeFilter = 'LIGHT'
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
                    if text_ops.CheckSuffix(object.name, tag.name_filter) is True:
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
                if text_ops.CheckSuffix(object.name, tag.name_filter) is True:
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
            typeFilter = 'LIGHT'
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
            if text_ops.CheckSuffix(object.name, tag.name_filter) is True:
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
        typeFilter = 'LIGHT'
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
                typeFilter = 'LIGHT'
            elif tag.object_type == '12':
                typeFilter = 'SPEAKER'

            #print("Type Filter Found...", typeFilter)

            if tag.object_type != '1':
                if search_object.type == typeFilter:
                    print("Object matches type filter")
                    return search_object

    print("Object doesn't match type filter")
    return None
