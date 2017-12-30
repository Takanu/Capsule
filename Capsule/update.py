
import bpy, bmesh, time
from math import *

from .tk_utils import groups as group_utils
from .tk_utils import select as select_utils

def CAP_Update_ObjectExport(self, context):
    """
    Updates the selected objects "Enable Export" status across UI elements.
    Note - This should only be used from the Enable Export UI tick, otherwise manually handle "Enable Export" status 
    assignment using "UpdateObjectList"
    """

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


def CAP_Update_SceneOrigin(self, context):
    """
    Updates the "Use Scene Origin" property for all selected objects.
    """
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


def CAP_Update_FocusObject(self, context):
    """
    Focuses the camera to a particular object, ensuring the object is clearly within the camera frame.  
    EDITME: The camera movement interpolation no longer works.
    """

    user_preferences = context.user_preferences
    addon_prefs = user_preferences.addons[__package__].preferences

    for object in context.scene.objects:
        if object.name == self.name:

            select_utils.FocusObject(object)

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


def CAP_Update_SelectObject(self, context):
    """
    Selects (but doesn't focus) the given object.
    """

    user_preferences = context.user_preferences
    addon_prefs = user_preferences.addons[__package__].preferences

    for object in context.scene.objects:
        if object.name == self.name:

            select_utils.ActivateObject(object)
            select_utils.SelectObject(object)

    return None


def CAP_Update_ObjectListName(self, context):
    """
    Updates the name of an object once edited from the list menu.
    Note - Do not use this in any other place apart from when an object is represented in a list.
    """

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

def CAP_Update_ObjectListExport(self, context):
    """
    Updates the "Enable Export" object status once changed from the list menu.
    Note - Do not use this in any other place apart from when an object is represented in a list.
    """

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

def CAP_Update_ObjectListSelect(self, context):
    """
    Used to turn off multi-select-enabled update functions if they were instead activated from a 
    list entry instead of another UI element.  Sneaky usability enhancements be here... <w<
    """
    user_preferences = context.user_preferences
    addon_prefs = user_preferences.addons[__package__].preferences

    if self.object_list_index != -1:
        print("Selection in list, turning off multi edit...")
        addon_prefs.object_multi_edit = False


def CAP_Update_ObjectRemoveFromList(self, context):
    """
    Used in a list to remove an object from both the export list, while disabling it's "Enable Export" status.
    """
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


def CAP_Update_LocationDefault(self, context):
    """
    Updates the object's Location Default property.
    """

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

def CAP_Update_ExportDefault(self, context):
    """
    Updates the object's Export Default property.
    """
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

def CAP_Update_Normals(self, context):
    """
    Updates the object's Normals property.
    FIXME: This needs to be categorised under a FBX-specific property panel
    """
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

def CAP_Update_ActionItemName(self, context):
    """
    Updates an animation actions name when edited from a list.
    """
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

def UpdateObjectList(scene, object, enableExport):
    """
    Used when properties are updated outside the scope of the Export List
    to ensure that all UI elements are kept in sync.
    """
    scn = scene.CAPScn
    print("Hey, this object is %s" % object)

    if object is None:
        return

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

    return None