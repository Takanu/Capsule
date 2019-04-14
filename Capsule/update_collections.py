
import bpy, bmesh, time
from math import *

from .tk_utils import collections as collection_utils
from .tk_utils import select as select_utils

def CAP_Update_CollectionExport(self, context):
    """
    Updates the selected groups' "Enable Export" status across UI elements.
    Note - This should only be used from the Enable Export UI tick, otherwise manually handle "Enable Export" status 
    assignment using "UpdateCollectionList"
    """

    preferences = context.preferences
    addon_prefs = preferences.addons[__package__].preferences
    scn = context.scene.CAPScn

    print("Inside EnableExport (Collection)")

    # If this was called from the actual UI element rather than another function,
    # we need to do stuff!
    if scn.enable_list_active == False and scn.enable_sel_active == False:
        print("Called from UI element")
        scn.enable_sel_active = True
        collected = []
        target = None
        value = False

        if addon_prefs.collection_multi_edit is True:
            # Acts as its own switch to prevent endless recursion
            if self == context.active_object.users_collection[0].CAPCol:
                current_collection = None

                if context.active_object.users_collection is not None:
                    current_collection = context.active_object.users_collection[0]

                collected.append(current_collection)

                for item in context.selected_objects:
                    for collection in item.users_collection:
                        collection_added = False

                        for found_group in collected:
                            if found_group.name == collection.name:
                                collection_added = True

                        if collection_added == False:
                            collected.append(collection)

                collected.remove(current_collection)
                target = current_collection
                value = self.enable_export

        # Otherwise, get information from the list
        else:
            item = scn.collection_list[scn.collection_list_index]
            print("Item Found:", item.name)
            for item in scene.objects:
                for collection in item.users_collection:
                    if collection.name == item.name:
                        target = collection

            value = self.enable_export

        # Obtain the value changed
        UpdateCollectionList(context.scene, target, value)

        # Run through the objects
        for collection in collected:
            collection.CAPCol.enable_export = value
            UpdateCollectionList(context.scene, collection, self.enable_export)

        scn.enable_sel_active = False
        scn.enable_list_active = False

    return None



def CAP_Update_FocusCollection(self, context):

    """
    Focuses the camera to a particular collection, moving it to ensure all objects are in the frame and can be seen clearly.
    EDITME: The camera movement interpolation no longer works.
    """

    preferences = context.preferences
    addon_prefs = preferences.addons[__package__].preferences

    for collection in collection_utils.GetSceneCollections(context.scene, True):
        if collection.name == self.name:

            bpy.ops.object.select_all(action='DESELECT')

            for object in collection.objects:
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

def CAP_Update_SelectCollection(self, context):

    """
    Selects (but doesn't focus) the given collection.
    """

    preferences = context.preferences
    addon_prefs = preferences.addons[__package__].preferences

    for collection in select_utils.GetSceneCollections(context.scene, True):
        if collection.name == self.name:

            #bpy.ops.object.select_all(action='DESELECT')

            for object in collection.objects:
                select_utils.ActivateObject(object)
                select_utils.SelectObject(object)

    return None

def CAP_Update_CollectionListName(self, context):
    """
    Updates the name of an collection once edited from the list menu.
    Note - Do not use this in any other place apart from when an object is represented in a list.
    """
    # Set the name of the item to the collection name
    for collection in collection_utils.GetSceneCollections(context.scene, True):
        print("Finding collection name to replace")
        if collection.name == self.prev_name:

            print("Found collection name ", collection.name)
            collection.name = self.name
            self.prev_name = collection.name

            print("Collection Name = ", collection.name)
            print("List Name = ", self.name)
            print("Prev Name = ", self.prev_name)

    return None

def CAP_Update_CollectionListExport(self, context):
    """
    Updates the "Enable Export" collection status once changed from the list menu.
    Note - Do not use this in any other place apart from when an object is represented in a list.
    """
    print("Changing Enable Export... (List)")

    preferences = context.preferences
    addon_prefs = preferences.addons[__package__].preferences
    scn = context.scene.CAPScn
    scn.enable_list_active = True

    if scn.enable_sel_active == False:

        # Set the name of the item to the collection name
        for collection in collection_utils.GetSceneCollections(context.scene, True):
            print("Finding collection name to replace")
            if collection.name == self.name:
                print("Found object name ", collection.name)
                collection.CAPCol.enable_export = self.enable_export

    scn.enable_sel_active = False
    scn.enable_list_active = False

    return None

def CAP_Update_CollectionListSelect(self, context):
    """
    Used to turn off multi-select-enabled update functions if they were instead activated from a 
    list entry instead of another UI element.  Sneaky usability enhancements be here... <w<
    """
    preferences = context.preferences
    addon_prefs = preferences.addons[__package__].preferences

    if self.collection_list_index != -1:
        print("Selection in list, turning off multi edit...")
        addon_prefs.collection_multi_edit = False


def CAP_Update_CollectionRemoveFromList(self, context):
    """
    Used in a list to remove a collection from both the export list, while disabling it's "Enable Export" status.
    """
    print("-----DELETING GROUP FROM LIST-----")
    i = 0
    scn = context.scene.CAPScn
    # To avoid issues within the list, the selected list item needs to be preserved.
    backupListIndex = scn.collection_list_index
    backupListLength = len(scn.collection_list)

    for item in scn.collection_list:
        if item.name == self.name:
            # Search through scene groups to untick export
            for sceneGroup in collection_utils.GetSceneCollections(context.scene, True):
                if sceneGroup.name == self.name:
                    print("Deleting", sceneGroup.name, "from the list.")
                    scn.enable_list_active = True

                    sceneGroup.CAPCol.enable_export = False
                    sceneGroup.CAPCol.in_export_list = False

            # Whether or not we find a successful match in the scene,
            # remove it from the list
            context.scene.CAPScn.collection_list.remove(i)

            # If the index is more than the list, bring it down one
            # to ensure a list item gets selected
            scn.collection_list_index = i

            if i == (backupListLength - 1):
                scn.collection_list_index = i - 1

            scn.enable_sel_active = False
            scn.enable_list_active = False
            return

        i += 1

def CAP_Update_CollectionRootObject(self, context):
    """
    Updates the "Collection Origin" property for all selected groups.
    """

    preferences = context.preferences
    addon_prefs = preferences.addons[__package__].preferences

    if addon_prefs.collection_multi_edit is True:

        # Acts as its own switch to prevent endless recursion
        if self == context.active_object.users_collection[0].CAPCol:
            current_collection = None
            
            if context.active_object.users_collection is not None:
                current_collection = context.active_object.users_collection[0]

            groups_found = collection_utils.GetObjectCollections(context.selected_objects)
            groups_found.remove(current_collection)

            # Obtain the value changed
            value = current_collection.CAPCol.root_object

            # Run through the objects
            for collection in groups_found:
                collection.CAPCol.root_object = value

    return None

def CAP_Update_CollectionLocationDefault(self, context):
    """
    Updates the object's Location Default property.
    """
    preferences = context.preferences
    addon_prefs = preferences.addons[__package__].preferences

    if addon_prefs.collection_multi_edit is True:

        # Acts as its own switch to prevent endless recursion
        if self == context.active_object.users_collection[0].CAPCol:
            current_collection = None

            if context.active_object.users_collection is not None:
                current_collection = context.active_object.users_collection[0]

            groups_found = collection_utils.GetObjectCollections(context.selected_objects)
            groups_found.remove(current_collection)

            # Obtain the value changed
            value = current_collection.CAPCol.location_default

            # Run through the objects
            for collection in groups_found:
                collection.CAPCol.location_default = value

    return None

def CAP_Update_CollectionExportDefault(self, context):
    """
    Updates the collection's Export Default property.
    """
    preferences = context.preferences
    addon_prefs = preferences.addons[__package__].preferences

    if addon_prefs.collection_multi_edit is True:

        # Acts as its own switch to prevent endless recursion
        if self == context.active_object.users_collection[0].CAPCol:
            current_collection = None

            if context.active_object.users_collection is not None:
                current_collection = context.active_object.users_collection[0]

            groups_found = collection_utils.GetObjectCollections(context.selected_objects)
            groups_found.remove(current_collection)

            # Obtain the value changed
            value = current_collection.CAPCol.export_default

            # Run through the objects
            for collection in groups_found:
                collection.CAPCol.export_default = value

    return None

def CAP_Update_CollectionNormals(self, context):
    """
    Updates the groups's Normals property.
    FIXME: This needs to be categorised under a FBX-specific property panel
    """
    preferences = context.preferences
    addon_prefs = preferences.addons[__package__].preferences

    if addon_prefs.collection_multi_edit is True:

        # Acts as its own switch to prevent endless recursion
        if self == context.active_object.users_collection[0].CAPCol:
            current_collection = None

            if context.active_object.users_collection is not None:
                current_collection = context.active_object.users_collection[0]

            groups_found = collection_utils.GetObjectCollections(context.selected_objects)
            groups_found.remove(current_collection)

            # Obtain the value changed
            value = current_collection.CAPCol.normals

            # Run through the objects
            for collection in groups_found:
                collection.CAPCol.normals = value

    return None

def UpdateCollectionList(scene, collection, enableExport):
    """
    Used when properties are updated outside the scope of the Export List
    to ensure that all UI elements are kept in sync.
    """
    scn = scene.CAPScn

    # Check a list entry for the collection doesn't already exist.
    for item in scene.CAPScn.collection_list:
        if item.name == collection.name:
            print("Changing", collection.name, "'s export from list.'")
            item.enable_export = enableExport
            return

    if enableExport is True:
        print("Adding", collection.name, "to list.")
        entry = scn.collection_list.add()
        entry.name = collection.name
        entry.prev_name = collection.name
        entry.enable_export = enableExport
        collection.CAPCol.in_export_list = True
