
import bpy, bmesh, time
from math import *

from .tk_utils import groups as group_utils
from .tk_utils import select as select_utils

def CAP_Update_GroupExport(self, context):
    """
    Updates the selected groups' "Enable Export" status across UI elements.
    Note - This should only be used from the Enable Export UI tick, otherwise manually handle "Enable Export" status 
    assignment using "UpdateGroupList"
    """

    user_preferences = context.user_preferences
    addon_prefs = user_preferences.addons[__package__].preferences
    scn = context.scene.CAPScn

    print("Inside EnableExport (Group)")

    # If this was called from the actual UI element rather than another function,
    # we need to do stuff!
    if scn.enable_list_active == False and scn.enable_sel_active == False:
        print("Called from UI element")
        scn.enable_sel_active = True
        collected = []
        target = None
        value = False

        if addon_prefs.group_multi_edit is True:
            # Acts as its own switch to prevent endless recursion
            if self == context.active_object.users_group[0].CAPGrp:
                currentGroup = None

                if context.active_object.users_group is not None:
                    currentGroup = context.active_object.users_group[0]

                collected.append(currentGroup)

                for item in context.selected_objects:
                    for group in item.users_group:
                        groupAdded = False

                        for found_group in collected:
                            if found_group.name == group.name:
                                groupAdded = True

                        if groupAdded == False:
                            collected.append(group)

                collected.remove(currentGroup)
                target = currentGroup
                value = self.enable_export

        # Otherwise, get information from the list
        else:
            item = scn.group_list[scn.group_list_index]
            print("Item Found:", item.name)
            for item in scene.objects:
                for group in item.users_group:
                    if group.name == item.name:
                        target = group

            value = self.enable_export

        # Obtain the value changed
        UpdateGroupList(context.scene, target, value)

        # Run through the objects
        for group in collected:
            group.CAPGrp.enable_export = value
            UpdateGroupList(context.scene, group, self.enable_export)

        scn.enable_sel_active = False
        scn.enable_list_active = False

    return None



def CAP_Update_FocusGroup(self, context):

    """
    Focuses the camera to a particular group, moving it to ensure all objects are in the frame and can be seen clearly.
    EDITME: The camera movement interpolation no longer works.
    """

    user_preferences = context.user_preferences
    addon_prefs = user_preferences.addons[__package__].preferences

    for group in group_utils.GetSceneGroups(context.scene, True):
        if group.name == self.name:

            bpy.ops.object.select_all(action='DESELECT')

            for object in group.objects:
                select_utils.SelectObject(object)

            # As the context won't be correct when the icon is clicked
            # We have to find the actual 3D view and override the context of the operator
            for area in bpy.context.screen.areas:
                if area.type == 'VIEW_3D':
                    for region in area.regions:
                        if region.type == 'WINDOW':
                            override = {'area': area, 
                                        'region': region, 
                                        'edit_object': bpy.context.edit_object, 
                                        'scene': bpy.context.scene, 
                                        'screen': bpy.context.screen, 
                                        'window': bpy.context.window}

                            bpy.ops.view3d.view_selected(override)

    return None

def CAP_Update_SelectGroup(self, context):

    """
    Selects (but doesn't focus) the given group.
    """

    user_preferences = context.user_preferences
    addon_prefs = user_preferences.addons[__package__].preferences

    for group in select_utils.GetSceneGroups(context.scene, True):
        if group.name == self.name:

            #bpy.ops.object.select_all(action='DESELECT')

            for object in group.objects:
                select_utils.ActivateObject(object)
                select_utils.SelectObject(object)

    return None

def CAP_Update_GroupListName(self, context):
    """
    Updates the name of an group once edited from the list menu.
    Note - Do not use this in any other place apart from when an object is represented in a list.
    """
    # Set the name of the item to the group name
    for group in group_utils.GetSceneGroups(context.scene, True):
        print("Finding group name to replace")
        if group.name == self.prev_name:

            print("Found group name ", group.name)
            group.name = self.name
            self.prev_name = group.name

            print("Group Name = ", group.name)
            print("List Name = ", self.name)
            print("Prev Name = ", self.prev_name)

    return None

def CAP_Update_GroupListExport(self, context):
    """
    Updates the "Enable Export" group status once changed from the list menu.
    Note - Do not use this in any other place apart from when an object is represented in a list.
    """
    print("Changing Enable Export... (List)")

    user_preferences = context.user_preferences
    addon_prefs = user_preferences.addons[__package__].preferences
    scn = context.scene.CAPScn
    scn.enable_list_active = True

    if scn.enable_sel_active == False:

        # Set the name of the item to the group name
        for group in group_utils.GetSceneGroups(context.scene, True):
            print("Finding group name to replace")
            if group.name == self.name:
                print("Found object name ", group.name)
                group.CAPGrp.enable_export = self.enable_export

    scn.enable_sel_active = False
    scn.enable_list_active = False

    return None

def CAP_Update_GroupListSelect(self, context):
    """
    Used to turn off multi-select-enabled update functions if they were instead activated from a 
    list entry instead of another UI element.  Sneaky usability enhancements be here... <w<
    """
    user_preferences = context.user_preferences
    addon_prefs = user_preferences.addons[__package__].preferences

    if self.group_list_index != -1:
        print("Selection in list, turning off multi edit...")
        addon_prefs.group_multi_edit = False


def CAP_Update_GroupRemoveFromList(self, context):
    """
    Used in a list to remove a group from both the export list, while disabling it's "Enable Export" status.
    """
    print("-----DELETING GROUP FROM LIST-----")
    i = 0
    scn = context.scene.CAPScn
    # To avoid issues within the list, the selected list item needs to be preserved.
    backupListIndex = scn.group_list_index
    backupListLength = len(scn.group_list)

    for item in scn.group_list:
        if item.name == self.name:
            # Search through scene groups to untick export
            for sceneGroup in group_utils.GetSceneGroups(context.scene, True):
                if sceneGroup.name == self.name:
                    print("Deleting", sceneGroup.name, "from the list.")
                    scn.enable_list_active = True

                    sceneGroup.CAPGrp.enable_export = False
                    sceneGroup.CAPGrp.in_export_list = False

            # Whether or not we find a successful match in the scene,
            # remove it from the list
            context.scene.CAPScn.group_list.remove(i)

            # If the index is more than the list, bring it down one
            # to ensure a list item gets selected
            scn.group_list_index = i

            if i == (backupListLength - 1):
                scn.group_list_index = i - 1

            scn.enable_sel_active = False
            scn.enable_list_active = False
            return

        i += 1

def CAP_Update_GroupRootObject(self, context):
    """
    Updates the "Group Origin" property for all selected groups.
    """

    user_preferences = context.user_preferences
    addon_prefs = user_preferences.addons[__package__].preferences

    if addon_prefs.group_multi_edit is True:

        # Acts as its own switch to prevent endless recursion
        if self == context.active_object.users_group[0].CAPGrp:
            currentGroup = None
            
            if context.active_object.users_group is not None:
                currentGroup = context.active_object.users_group[0]

            groups_found = group_utils.GetObjectGroups(context.selected_objects)
            groups_found.remove(currentGroup)

            # Obtain the value changed
            value = currentGroup.CAPGrp.root_object

            # Run through the objects
            for group in groups_found:
                group.CAPGrp.root_object = value

    return None

def CAP_Update_GroupLocationDefault(self, context):
    """
    Updates the object's Location Default property.
    """
    user_preferences = context.user_preferences
    addon_prefs = user_preferences.addons[__package__].preferences

    if addon_prefs.group_multi_edit is True:

        # Acts as its own switch to prevent endless recursion
        if self == context.active_object.users_group[0].CAPGrp:
            currentGroup = None

            if context.active_object.users_group is not None:
                currentGroup = context.active_object.users_group[0]

            groups_found = group_utils.GetObjectGroups(context.selected_objects)
            groups_found.remove(currentGroup)

            # Obtain the value changed
            value = currentGroup.CAPGrp.location_default

            # Run through the objects
            for group in groups_found:
                group.CAPGrp.location_default = value

    return None

def CAP_Update_GroupExportDefault(self, context):
    """
    Updates the group's Export Default property.
    """
    user_preferences = context.user_preferences
    addon_prefs = user_preferences.addons[__package__].preferences

    if addon_prefs.group_multi_edit is True:

        # Acts as its own switch to prevent endless recursion
        if self == context.active_object.users_group[0].CAPGrp:
            currentGroup = None

            if context.active_object.users_group is not None:
                currentGroup = context.active_object.users_group[0]

            groups_found = group_utils.GetObjectGroups(context.selected_objects)
            groups_found.remove(currentGroup)

            # Obtain the value changed
            value = currentGroup.CAPGrp.export_default

            # Run through the objects
            for group in groups_found:
                group.CAPGrp.export_default = value

    return None

def CAP_Update_GroupNormals(self, context):
    """
    Updates the groups's Normals property.
    FIXME: This needs to be categorised under a FBX-specific property panel
    """
    user_preferences = context.user_preferences
    addon_prefs = user_preferences.addons[__package__].preferences

    if addon_prefs.group_multi_edit is True:

        # Acts as its own switch to prevent endless recursion
        if self == context.active_object.users_group[0].CAPGrp:
            currentGroup = None

            if context.active_object.users_group is not None:
                currentGroup = context.active_object.users_group[0]

            groups_found = group_utils.GetObjectGroups(context.selected_objects)
            groups_found.remove(currentGroup)

            # Obtain the value changed
            value = currentGroup.CAPGrp.normals

            # Run through the objects
            for group in groups_found:
                group.CAPGrp.normals = value

    return None

def UpdateGroupList(scene, group, enableExport):
    """
    Used when properties are updated outside the scope of the Export List
    to ensure that all UI elements are kept in sync.
    """
    scn = scene.CAPScn

    # Check a list entry for the group doesn't already exist.
    for item in scene.CAPScn.group_list:
        if item.name == group.name:
            print("Changing", group.name, "'s export from list.'")
            item.enable_export = enableExport
            return

    if enableExport is True:
        print("Adding", group.name, "to list.")
        entry = scn.group_list.add()
        entry.name = group.name
        entry.prev_name = group.name
        entry.enable_export = enableExport
        group.CAPGrp.in_export_list = True
