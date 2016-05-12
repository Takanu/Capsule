
import bpy, bmesh, time
from .definitions import SelectObject, FocusObject, ActivateObject, CheckSuffix, CheckForTags, GetSceneGroups
from math import *

def Update_EnableExport(self, context):

    user_preferences = context.user_preferences
    addon_prefs = user_preferences.addons[__package__].preferences
    scn = context.scene.CAPScn

    print("Inside EnableExport (Object)")

    # If this was called from the actual UI element rather than another function,
    # we need to do stuff!
    print(scn.enable_list_active, scn.enable_sel_active)
    if scn.enable_list_active == False and scn.enable_sel_active == False:
        print("Called from UI element")
        scn.enable_sel_active = True
        collected = []
        target = None
        value = False

        # If the selection has come from the scene, get data from inside the scene
        if addon_prefs.object_multi_edit is True:
            # Acts as its own switch to prevent endless recursion
            if self == context.active_object.CAPObj:
                print("Changing Export...", context.active_object.name)

                for sel in context.selected_objects:
                    if sel.name != context.active_object.name:
                        collected.append(sel)

                # Obtain the value changed
                target = context.active_object
                value = self.enable_export

        # Otherwise, get information from the list
        else:
            item = scn.object_list[scn.object_list_index]
            print("Item Found:", item.name)
            target = scene.objects[item.name]
            value = self.enable_export

        # Update the list associated with the object
        UpdateObjectList(context.scene, target, value)

        # Run through any collected objects to also update them.
        for item in collected:
            item.CAPObj.enable_export = value
            UpdateObjectList(context.scene, item, value)

        scn.enable_sel_active = False
        scn.enable_list_active = False

    return None


def Update_SceneOrigin(self, context):

    user_preferences = context.user_preferences
    addon_prefs = user_preferences.addons[__package__].preferences

    if addon_prefs.object_multi_edit is True:
        # Acts as its own switch to prevent endless recursion
        if self == context.active_object.CAPObj:

            # Keep a record of the selected objects to update
            selected = []

            for sel in context.selected_objects:
                if sel.name != context.active_object.name:
                    selected.append(sel)

            # Obtain the value changed
            value = self.use_scene_origin

            # Run through the objects
            for object in selected:
                object.CAPObj.use_scene_origin = value

    return None


def Update_LocationDefault(self, context):

    user_preferences = context.user_preferences
    addon_prefs = user_preferences.addons[__package__].preferences

    if addon_prefs.object_multi_edit is True:
        # Acts as its own switch to prevent endless recursion
        if self == context.active_object.CAPObj:
            print(context.active_object.name)

            # Keep a record of the selected objects to update
            selected = []

            for sel in context.selected_objects:
                if sel.name != context.active_object.name:
                    selected.append(sel)

            # Obtain the value changed
            value = self.location_default

            # Run through the objects
            for object in selected:
                object.CAPObj.location_default = value

    return None

def Update_ExportDefault(self, context):

    user_preferences = context.user_preferences
    addon_prefs = user_preferences.addons[__package__].preferences

    if addon_prefs.object_multi_edit is True:
        # Acts as its own switch to prevent endless recursion
        if self == context.active_object.CAPObj:

            # Keep a record of the selected objects to update
            selected = []

            for sel in context.selected_objects:
                if sel.name != context.active_object.name:
                    selected.append(sel)

            # Obtain the value changed
            value = self.export_default

            # Run through the objects
            for object in selected:
                object.CAPObj.export_default = value

    return None

def Update_Normals(self, context):

    user_preferences = context.user_preferences
    addon_prefs = user_preferences.addons[__package__].preferences

    if addon_prefs.object_multi_edit is True:
        # Acts as its own switch to prevent endless recursion
        if self == context.active_object.CAPObj:

            # Keep a record of the selected objects to update
            selected = []

            for sel in context.selected_objects:
                if sel.name != context.active_object.name:
                    selected.append(sel)

            # Obtain the value changed
            value = self.normals

            # Run through the objects
            for object in selected:
                object.CAPObj.normals = value

    return None

def Update_ActionItemName(self, context):

    active = context.active_object
    print(">>> Changing Action Name <<<")
    print(self)

    if active.animation_data is not None:
        animData = active.animation_data
        print("Checking Object Animation Names...")

        if animData.action is not None:
            if animData.action.name == self.prev_name:
                animData.action.name = self.name
                self.prev_name = self.name
                return None

        for nla in active.animation_data.nla_tracks:
            print("Checking NLA...", nla, nla.name)
            if nla.name == self.prev_name:
                nla.name = self.name
                self.prev_name = self.name
                return None

    modType = {'ARMATURE'}

    for modifier in active.modifiers:
        if modifier.type in modType:
            armature = modifier.object

    if armature is not None:
        if armature.animation_data is not None:
            animData = armature.animation_data
            print("Checking Armature Animation Names...")

            if animData.action is not None:
                if animData.action.name == self.prev_name:
                    animData.action.name = self.name
                    self.prev_name = self.name
                    return None

            for nla in animData.nla_tracks:
                if nla.name == self.prev_name:
                    nla.name = self.name
                    self.prev_name = self.name
                    return None

    print("No name could be changed for action", self.prev_name, ".  Oh no!")

    return None

def Focus_Object(self, context):
    user_preferences = context.user_preferences
    addon_prefs = user_preferences.addons[__package__].preferences

    for object in context.scene.objects:
        if object.name == self.name:

            FocusObject(object)

            # As the context won't be correct when the icon is clicked
            # We have to find the actual 3D view and override the context of the operator
            for area in bpy.context.screen.areas:
                if area.type == 'VIEW_3D':
                    for region in area.regions:
                        if region.type == 'WINDOW':
                            override = {'area': area, 'region': region, 'edit_object': bpy.context.edit_object, 'scene': bpy.context.scene, 'screen': bpy.context.screen, 'window': bpy.context.window}
                            bpy.ops.view3d.view_selected(override)
    return None

def Focus_Group(self, context):
    user_preferences = context.user_preferences
    addon_prefs = user_preferences.addons[__package__].preferences

    for group in GetSceneGroups(context.scene, True):
        if group.name == self.name:

            bpy.ops.object.select_all(action='DESELECT')

            for object in group.objects:
                SelectObject(object)

            # As the context won't be correct when the icon is clicked
            # We have to find the actual 3D view and override the context of the operator
            for area in bpy.context.screen.areas:
                if area.type == 'VIEW_3D':
                    for region in area.regions:
                        if region.type == 'WINDOW':
                            override = {'area': area, 'region': region, 'edit_object': bpy.context.edit_object, 'scene': bpy.context.scene, 'screen': bpy.context.screen, 'window': bpy.context.window}
                            bpy.ops.view3d.view_selected(override)

    return None

def Select_Object(self, context):
    user_preferences = context.user_preferences
    addon_prefs = user_preferences.addons[__package__].preferences

    for object in context.scene.objects:
        if object.name == self.name:

            ActivateObject(object)
            SelectObject(object)

    return None

def Select_Group(self, context):
    user_preferences = context.user_preferences
    addon_prefs = user_preferences.addons[__package__].preferences

    for group in GetSceneGroups(context.scene, True):
        if group.name == self.name:

            #bpy.ops.object.select_all(action='DESELECT')

            for object in group.objects:
                ActivateObject(object)
                SelectObject(object)

    return None



def Update_GroupExport(self, context):
    user_preferences = context.user_preferences
    addon_prefs = user_preferences.addons[__package__].preferences
    scn = context.scene.CAPScn

    print("Inside EnableExport (Object)")

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


def Update_GroupRootObject(self, context):
    user_preferences = context.user_preferences
    addon_prefs = user_preferences.addons[__package__].preferences

    if addon_prefs.group_multi_edit is True:
        # Acts as its own switch to prevent endless recursion
        if self == context.active_object.users_group[0].CAPGrp:
            currentGroup = None
            if context.active_object.users_group is not None:
                currentGroup = context.active_object.users_group[0]

            groups_found = []
            groups_found.append(currentGroup)

            for item in context.selected_objects:
                for group in item.users_group:
                    groupAdded = False

                    for found_group in groups_found:
                        if found_group.name == group.name:
                            groupAdded = True

                    if groupAdded == False:
                        print("")
                        groups_found.append(group)

            groups_found.remove(currentGroup)

            # Obtain the value changed
            value = currentGroup.CAPGrp.root_object

            # Run through the objects
            for group in groups_found:
                group.CAPGrp.root_object = value

    return None

def Update_GroupExportDefault(self, context):
    user_preferences = context.user_preferences
    addon_prefs = user_preferences.addons[__package__].preferences

    if addon_prefs.group_multi_edit is True:
        # Acts as its own switch to prevent endless recursion
        if self == context.active_object.users_group[0].CAPGrp:
            currentGroup = None
            if context.active_object.users_group is not None:
                currentGroup = context.active_object.users_group[0]

            groups_found = []
            groups_found.append(currentGroup)

            for item in context.selected_objects:
                for group in item.users_group:
                    groupAdded = False

                    for found_group in groups_found:
                        if found_group.name == group.name:
                            groupAdded = True

                    if groupAdded == False:
                        print("")
                        groups_found.append(group)

            groups_found.remove(currentGroup)

            # Obtain the value changed
            value = currentGroup.CAPGrp.export_default

            # Run through the objects
            for group in groups_found:
                group.CAPGrp.export_default = value

    return None

def Update_GroupLocationDefault(self, context):
    user_preferences = context.user_preferences
    addon_prefs = user_preferences.addons[__package__].preferences

    if addon_prefs.group_multi_edit is True:
        # Acts as its own switch to prevent endless recursion
        if self == context.active_object.users_group[0].CAPGrp:
            currentGroup = None
            if context.active_object.users_group is not None:
                currentGroup = context.active_object.users_group[0]

            groups_found = []
            groups_found.append(currentGroup)

            for item in context.selected_objects:
                for group in item.users_group:
                    groupAdded = False

                    for found_group in groups_found:
                        if found_group.name == group.name:
                            groupAdded = True

                    if groupAdded == False:
                        print("")
                        groups_found.append(group)

            groups_found.remove(currentGroup)

            # Obtain the value changed
            value = currentGroup.CAPGrp.location_default

            # Run through the objects
            for group in groups_found:
                group.CAPGrp.location_default = value

    return None

def Update_GroupNormals(self, context):
    user_preferences = context.user_preferences
    addon_prefs = user_preferences.addons[__package__].preferences

    if addon_prefs.group_multi_edit is True:
        # Acts as its own switch to prevent endless recursion
        if self == context.active_object.users_group[0].CAPGrp:
            currentGroup = None
            if context.active_object.users_group is not None:
                currentGroup = context.active_object.users_group[0]

            groups_found = []
            groups_found.append(currentGroup)

            for item in context.selected_objects:
                for group in item.users_group:
                    groupAdded = False

                    for found_group in groups_found:
                        if found_group.name == group.name:
                            groupAdded = True

                    if groupAdded == False:
                        print("")
                        groups_found.append(group)

            groups_found.remove(currentGroup)

            # Obtain the value changed
            value = currentGroup.CAPGrp.normals

            # Run through the objects
            for group in groups_found:
                group.CAPGrp.normals = value

    return None

def Update_ObjectItemName(self, context):

    print("Finding object name to replace")
    scn = context.scene.CAPScn

    # Set the name of the item to the group name
    for item in context.scene.objects:
        if item.name == self.prev_name:
            print("Found object name ", item.name)
            item.name = self.name
            self.prev_name = item.name

            print("object Name = ", item.name)
            print("List Name = ", self.name)
            print("Prev Name = ", self.prev_name)

    return None

def Update_ObjectItemExport(self, context):

    print("Changing Enable Export... (List)")

    user_preferences = context.user_preferences
    addon_prefs = user_preferences.addons[__package__].preferences
    scn = context.scene.CAPScn
    scn.enable_list_active = True

    if scn.enable_sel_active == False:
        print("Rawr")
        # Set the name of the item to the group name
        for item in context.scene.objects:
            if item.name == self.name:
                print("Found object name ", item.name)
                item.CAPObj.enable_export = self.enable_export

    scn.enable_sel_active = False
    scn.enable_list_active = False
    return None

def Update_GroupItemName(self, context):

    # Set the name of the item to the group name
    for group in GetSceneGroups(context.scene, True):
        print("Finding group name to replace")
        if group.name == self.prev_name:

            print("Found group name ", group.name)
            group.name = self.name
            self.prev_name = group.name

            print("Group Name = ", group.name)
            print("List Name = ", self.name)
            print("Prev Name = ", self.prev_name)

    return None

def Update_GroupItemExport(self, context):

    print("Changing Enable Export... (List)")

    user_preferences = context.user_preferences
    addon_prefs = user_preferences.addons[__package__].preferences
    scn = context.scene.CAPScn
    scn.enable_list_active = True

    if scn.enable_sel_active == False:

        # Set the name of the item to the group name
        for group in GetSceneGroups(context.scene, True):
            print("Finding group name to replace")
            if group.name == self.name:
                print("Found object name ", group.name)
                group.CAPGrp.enable_export = self.enable_export

    scn.enable_sel_active = False
    scn.enable_list_active = False

    return None

def Update_ObjectListSelect(self, context):
    user_preferences = context.user_preferences
    addon_prefs = user_preferences.addons[__package__].preferences

    if self.object_list_index != -1:
        print("Selection in list, turning off multi edit...")
        addon_prefs.object_multi_edit = False

def Update_GroupListSelect(self, context):
    user_preferences = context.user_preferences
    addon_prefs = user_preferences.addons[__package__].preferences

    if self.group_list_index != -1:
        print("Selection in list, turning off multi edit...")
        addon_prefs.group_multi_edit = False

def Update_ObjectRemoveFromList(self, context):
    print("-----DELETING OBJECT FROM LIST-----")
    i = 0
    scn = context.scene.CAPScn
    # To avoid issues within the list, the selected list item needs to be preserved.
    backupListIndex = scn.object_list_index
    backupListLength = len(scn.object_list)

    # Search through the object list to find a matching name
    for item in scn.object_list:
        if item.name == self.name:
            # Search through scene objects to untick export
            for sceneObj in context.scene.objects:
                if sceneObj.name == self.name:
                    print("Deleting", sceneObj.name, "from the list.")
                    scn.enable_list_active = True

                    sceneObj.CAPObj.enable_export = False
                    sceneObj.CAPObj.in_export_list = False

            # Whether or not we find a successful match in the scene,
            # remove it from the list
            context.scene.CAPScn.object_list.remove(i)

            # Set the new list index
            scn.object_list_index = i

            # If the index is more than the list, bring it down one
            # to ensure a list item gets selected
            if i == (backupListLength - 1):
                scn.object_list_index = i - 1

            scn.enable_sel_active = False
            scn.enable_list_active = False
            return

        i += 1


def Update_GroupRemoveFromList(self, context):
    print("-----DELETING GROUP FROM LIST-----")
    i = 0
    scn = context.scene.CAPScn
    # To avoid issues within the list, the selected list item needs to be preserved.
    backupListIndex = scn.group_list_index
    backupListLength = len(scn.group_list)

    for item in scn.group_list:
        if item.name == self.name:
            # Search through scene groups to untick export
            for sceneGroup in GetSceneGroups(context.scene, True):
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


def UpdateObjectList(scene, object, enableExport):
    scn = scene.CAPScn

    # Check a list entry for the object doesn't already exist.
    for item in scene.CAPScn.object_list:
        if item.name == object.name:
            print("Changing", object.name, "'s export from list.'")
            item.enable_export = enableExport
            return

    # If an entry couldn't be found in the list, add it.
    if enableExport is True:
        print("Adding", object.name, "to list.")
        entry = scn.object_list.add()
        entry.name = object.name
        entry.prev_name = object.name
        entry.enable_export = enableExport

        object.CAPObj.in_export_list = True

def UpdateGroupList(scene, group, enableExport):
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
