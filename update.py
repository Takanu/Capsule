import bpy, bmesh, time
from .definitions import SelectObject, FocusObject, ActivateObject
from math import *

def Update_EnableExport(self, context):

    user_preferences = context.user_preferences
    addon_prefs = user_preferences.addons["GEX"].preferences

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
            if object.name.find(addon_prefs.lp_tag) != -1:
                object.GXObj.enable_export = enableExport

    return None


def Update_AutoAssign(self, context):

    user_preferences = context.user_preferences
    addon_prefs = user_preferences.addons["GEX"].preferences

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
            if object.name.find(addon_prefs.lp_tag) != -1:
                object.GXObj.auto_assign = autoAssign

    return None


def Update_LocationDefault(self, context):

    user_preferences = context.user_preferences
    addon_prefs = user_preferences.addons["GEX"].preferences

    # Acts as its own switch to prevent endless recursion
    if self == context.active_object.GXObj:

        # Keep a record of the selected objects to update
        selected = []

        for sel in context.selected_objects:
            if sel.name != context.active_object.name:
                selected.append(sel)

        # Obtain the value changed
        value = self.location_default

        # Run through the objects
        for object in selected:
            if object.name.find(addon_prefs.lp_tag) != -1:
                object.GXObj.location_default = value

    return None

def Update_ExportDefault(self, context):

    user_preferences = context.user_preferences
    addon_prefs = user_preferences.addons["GEX"].preferences

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
            if object.name.find(addon_prefs.lp_tag) != -1:
                object.GXObj.export_default = value

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
