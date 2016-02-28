import bpy, bmesh, time
from .definitions import SelectObject, FocusObject, ActivateObject, CheckSuffix, CheckForTags
from math import *

def Update_EnableExport(self, context):

    user_preferences = context.user_preferences
    addon_prefs = user_preferences.addons[__package__].preferences

    # Acts as its own switch to prevent endless recursion
    if self == context.active_object.GXObj:

        # Keep a record of the selected objects to update
        selected = []

        for sel in context.selected_objects:
            if sel.name != context.active_object.name:
                selected.append(sel)

        # Obtain the value changed
        enableExport = self.enable_export

        # Run through the objects
        for object in selected:
            if CheckForTags(context, object.name) is False:
                object.GXObj.enable_export = enableExport

            elif CheckSuffix(object.name, addon_prefs.lp_tag) is True:
                object.GXObj.enable_export = enableExport

    return None


def Update_AutoAssign(self, context):

    user_preferences = context.user_preferences
    addon_prefs = user_preferences.addons[__package__].preferences

    # Acts as its own switch to prevent endless recursion
    if self == context.active_object.GXObj:

        # Keep a record of the selected objects to update
        selected = []

        for sel in context.selected_objects:
            if sel.name != context.active_object.name:
                selected.append(sel)

        # Obtain the value changed
        autoAssign = self.auto_assign

        # Run through the objects
        for object in selected:
            if CheckForTags(context, object.name) is False:
                object.GXObj.auto_assign = autoAssign

            elif CheckSuffix(object.name, addon_prefs.lp_tag) is True:
                object.GXObj.auto_assign = autoAssign

    return None


def Update_LocationDefault(self, context):

    user_preferences = context.user_preferences
    addon_prefs = user_preferences.addons[__package__].preferences

    # Acts as its own switch to prevent endless recursion
    if self == context.active_object.GXObj:
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
            print(object.name)
            if CheckForTags(context, object.name) is False:
                print("Passing down object variable")
                object.GXObj.location_default = value

            elif CheckSuffix(object.name, addon_prefs.lp_tag) is True:
                print("Passing down object variable")
                object.GXObj.location_default = value

    return None

def Update_ExportDefault(self, context):

    user_preferences = context.user_preferences
    addon_prefs = user_preferences.addons[__package__].preferences

    # Acts as its own switch to prevent endless recursion
    if self == context.active_object.GXObj:

        # Keep a record of the selected objects to update
        selected = []

        for sel in context.selected_objects:
            if sel.name != context.active_object.name:
                selected.append(sel)

        # Obtain the value changed
        value = self.export_default

        # Run through the objects
        for object in selected:
            if CheckForTags(context, object.name) is False:
                object.GXObj.export_default = value

            elif CheckSuffix(object.name, addon_prefs.lp_tag) is True:
                object.GXObj.export_default = value

    return None

def Update_Normals(self, context):

    user_preferences = context.user_preferences
    addon_prefs = user_preferences.addons[__package__].preferences

    # Acts as its own switch to prevent endless recursion
    if self == context.active_object.GXObj:

        # Keep a record of the selected objects to update
        selected = []

        for sel in context.selected_objects:
            if sel.name != context.active_object.name:
                selected.append(sel)

        # Obtain the value changed
        value = self.normals

        # Run through the objects
        for object in selected:
            if CheckForTags(context, object.name) is False:
                object.GXObj.normals = value

            elif CheckSuffix(object.name, addon_prefs.lp_tag) is True:
                object.GXObj.normals = value

    return None


def Update_ObjectItemName(self, context):

    print("Finding object name to replace")

    # Set the name of the item to the group name
    for object in context.scene.objects:
        if object.name == self.prev_name:

            print("Found object name ", object.name)
            object.name = self.name
            self.prev_name = object.name

            print("object Name = ", object.name)
            print("List Name = ", self.name)
            print("Prev Name = ", self.prev_name)

    return None

def Update_ObjectItemExport(self, context):

    print("Finding object name to replace")

    # Set the name of the item to the group name
    for object in context.scene.objects:
        if object.name == self.name:

            print("Found object name ", object.name)
            object.GXObj.enable_export = self.enable_export


    return None

def Update_GroupItemName(self, context):

    # Set the name of the item to the group name
    for group in bpy.data.groups:
        print("Finding group name to replace")
        if group.name == self.prev_name:

            print("Found group name ", group.name)
            group.name = self.name
            self.prev_name = group.name

            print("Group Name = ", group.name)
            print("List Name = ", self.name)
            print("Prev Name = ", self.prev_name)

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
                            override = {'area': area, 'region': region, 'edit_object': bpy.context.edit_object}
                            bpy.ops.view3d.view_selected(override)
    return None


def Focus_Group(self, context):
    user_preferences = context.user_preferences
    addon_prefs = user_preferences.addons[__package__].preferences

    for group in bpy.data.groups:
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
                            override = {'area': area, 'region': region, 'edit_object': bpy.context.edit_object}
                            bpy.ops.view3d.view_selected(override)

    return None


def Update_GroupRoot(self, context):
    user_preferences = context.user_preferences
    addon_prefs = user_preferences.addons[__package__].preferences

    # Acts as its own switch to prevent endless recursion
    if self == context.active_object.GXObj:

        groups_found = []

        for item in context.selected_objects:
            for group in item.users_group:
                groupAdded = False

                for found_group in groups_found:
                    if found_group.name == group.name:
                        groupAdded = True

                if groupAdded == False:
                    groups_found.append(group)

        # Run through the objects
        for object in selected:
            if CheckForTags(context, object.name) is False:
                object.GXObj.export_default = value

            elif CheckSuffix(object.name, addon_prefs.lp_tag) is True:
                object.GXObj.export_default = value

    return None

def Update_GroupMultiEdit(self, context):

    bpy.ops.scene.gx_group_multiedit_warning()

    return None

def Update_GroupSelectionEdit(self, context):

    bpy.ops.scene.gx_ref_selected_groups()

    return None
