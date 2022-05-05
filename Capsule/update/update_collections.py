
import bpy, bmesh, time
from math import *

from ..tk_utils import search as search_utils
from ..tk_utils import select as select_utils
from ..tk_utils import object_ops

# COLLECTION DATA PROXY PROPERTIES
# /////////////////////////////////////////////////
# /////////////////////////////////////////////////


def CAP_Update_ProxyCollectionExport(self, context):
    """
    Used for selection editing to update all properties in the current selection.
    """

    preferences = context.preferences
    addon_prefs = preferences.addons['Capsule'].preferences
    scn = context.scene.CAPScn
    proxy = context.scene.CAPProxy

    # If updates are disabled, return early.
    if proxy.disable_updates == True:
        return

    collected = search_utils.GetEditableCollections(context)
    value = proxy.col_enable_export
    # print("Current value - ", value)

    # Run through the objects
    # TODO: Not sure why a collection here would become invalid
    for collection in collected:
        if collection is not None:
            # print(collection)
            collection.CAPCol.enable_export = value
            UpdateCollectionList(context.scene, collection, value)

    return None

def CAP_Update_ProxyCollectionOriginPoint(self, context):
    """
    Updates the "Collection Origin" property for all selected groups.
    """

    preferences = context.preferences
    addon_prefs = preferences.addons['Capsule'].preferences
    proxy = context.scene.CAPProxy
    
    # If updates are disabled, return early.
    if proxy.disable_updates == True:
        return

    collected = search_utils.GetEditableCollections(context)
    value = proxy.col_origin_point

    # Run through the objects
    for collection in collected:
        collection.CAPCol.origin_point = value

    return None


def CAP_Update_ProxyCollectionRootObject(self, context):
    """
    Updates the "Collection Origin" property for all selected groups.
    """

    preferences = context.preferences
    addon_prefs = preferences.addons['Capsule'].preferences
    proxy = context.scene.CAPProxy
    
    # If updates are disabled, return early.
    if proxy.disable_updates == True:
        return

    collected = search_utils.GetEditableCollections(context)
    value = proxy.col_root_object

    # Run through the objects
    for collection in collected:
        collection.CAPCol.root_object = value

    return None


def CAP_Update_ProxyCollectionChildExportOption(self, context):
    """
    Updates the "Child Export Options" property for all selected groups.
    """

    preferences = context.preferences
    addon_prefs = preferences.addons['Capsule'].preferences
    proxy = context.scene.CAPProxy
    
    # If updates are disabled, return early.
    if proxy.disable_updates == True:
        return

    collected = search_utils.GetEditableCollections(context)
    value = proxy.col_child_export_option

    # Run through the objects
    for collection in collected:
        collection.CAPCol.child_export_option = value

    return None


def CAP_Update_ProxyCollectionLocationPreset(self, context):
    """
    Updates the object's Location Default property.
    """
    preferences = context.preferences
    addon_prefs = preferences.addons['Capsule'].preferences
    proxy = context.scene.CAPProxy
    
    # If updates are disabled, return early.
    if proxy.disable_updates == True:
        return

    # If updates are disabled, return early.
    if proxy.disable_updates == True:
        return

    collected = search_utils.GetEditableCollections(context)
    value = proxy.col_location_preset

    # Run through the objects
    for collection in collected:
        collection.CAPCol.location_preset = value

    return None

def CAP_Update_ProxyCollectionExportPreset(self, context):
    """
    Updates the collection's Export Default property.
    """
    preferences = context.preferences
    addon_prefs = preferences.addons['Capsule'].preferences
    proxy = context.scene.CAPProxy
    
    # If updates are disabled, return early.
    if proxy.disable_updates == True:
        return

    # If updates are disabled, return early.
    if proxy.disable_updates == True:
        return

    collected = search_utils.GetEditableCollections(context)
    value = proxy.col_export_preset

    # Run through the objects
    for collection in collected:
        collection.CAPCol.export_preset = value

    return None

def CAP_Update_ProxyCollectionOverride(self, context):
    """
    Updates the collection's Pack property.
    """
    preferences = context.preferences
    addon_prefs = preferences.addons['Capsule'].preferences
    proxy = context.scene.CAPProxy
    
    # If updates are disabled, return early.
    if proxy.disable_updates == True:
        return

    # If updates are disabled, return early.
    if proxy.disable_updates == True:
        return

    collected = search_utils.GetEditableCollections(context)
    value = proxy.col_pack_script

    # Run through the objects
    for collection in collected:
        collection.CAPCol.pack_script = value

    return None


# COLLECTION LIST PROPERTIES
# /////////////////////////////////////////////////
# /////////////////////////////////////////////////

def UpdateCollectionList(scene, collection, enableExport):
    """
    Used when properties are updated outside the scope of the Export List
    to ensure that all UI elements are kept in sync.
    """
    scn = scene.CAPScn

    # Check a list entry for the collection doesn't already exist.

    for item in scene.CAPScn.collection_list:
        if item:
            if item.collection:
                if item.collection.name == collection.name:
                    #print("Changing", collection.name, "'s export from list.'")
                    item.enable_export = enableExport
                    return

    if enableExport is True:
        #print("Adding", collection.name, "to list.")
        entry = scn.collection_list.add()
        entry.collection = collection
        entry.enable_export = enableExport
        collection.CAPCol.in_export_list = True


def CAP_Update_FocusCollection(self, context):

    """
    Focuses the camera to a particular collection, moving it to ensure all objects are in the frame and can be seen clearly.
    TODO 2.0: The camera movement interpolation no longer works.
    """
    bpy.ops.object.select_all(action= 'DESELECT')

    for object in self.collection.objects:
        object.select_set(True)
        bpy.context.view_layer.objects.active = object


    # As the context won't be correct when the icon is clicked
    # We have to find the actual 3D view and override the context of the operator

    # Old 3.1 code juussst in case I need it, deprecated in 3.2.
    # for area in bpy.context.screen.areas:
    #     if area.type == 'VIEW_3D':
    #         for region in area.regions:
    #             if region.type == 'WINDOW':
    #                 override = {'area': area, 
    #                             'region': region, 
    #                             'edit_object': bpy.context.edit_object, 
    #                             'scene': bpy.context.scene, 
    #                             'screen': bpy.context.screen, 
    #                             'window': bpy.context.window}
    #                 
    #                 bpy.ops.view3d.view_selected(override)

    override = object_ops.Find3DViewContext()
    
    with context.temp_override(window = override['window'], area = override['area'], 
            region = override['region']):

            bpy.ops.view3d.view_selected()

    return None

def CAP_Update_SelectCollection(self, context):

    """
    Selects (but doesn't focus) the given collection.
    """
    bpy.ops.object.select_all(action= 'DESELECT')

    for object in self.collection.objects:
        object.select_set(True)
        bpy.context.view_layer.objects.active = object

    return None


def CAP_Update_CollectionListExport(self, context):
    """
    Updates the "Enable Export" collection status once changed from the list menu.
    Note - Do not use this in any other place apart from when an object is represented in a list.
    """

    self.collection.CAPCol.enable_export = self.enable_export
    return None


def CAP_Update_CollectionListRemove(self, context):
    """
    Used in a list to remove a collection from both the export list, while disabling it's "Enable Export" status.
    """

    print(self)

    #print("-----DELETING GROUP FROM LIST-----")
    i = 0
    scn = context.scene.CAPScn
    # To avoid issues within the list, the selected list item needs to be preserved.
    backupListIndex = scn.collection_list_index
    backupListLength = len(scn.collection_list)

    # If the list item is dead, remove it now and forget about the rest.
    # if self is None or self.collection is None:


    for item in scn.collection_list:
        if item.collection is not None:
            if item.collection.name == self.collection.name:

                self.collection.CAPCol.enable_export = False
                self.collection.CAPCol.in_export_list = False

                # Whether or not we find a successful match in the scene,
                # remove it from the list
                context.scene.CAPScn.collection_list.remove(i)

                # If the index is more than the list, bring it down one
                # to ensure a list item gets selected
                scn.collection_list_index = i

                if i == (backupListLength - 1):
                    scn.collection_list_index = i - 1

                return

            i += 1