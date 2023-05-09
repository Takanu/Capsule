
import bpy, bmesh, time
from math import *

from .update_list import UpdateCollectionList

# COLLECTION DATA PROXY PROPERTIES
# /////////////////////////////////////////////////
# /////////////////////////////////////////////////


def CAP_Update_ProxyCol_EnableExport(self, context):
    """
    Updates the "Enable Export" property for all selected collections
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

def CAP_Update_ProxyCol_OriginPoint(self, context):
    """
    Updates the Origin Point property for all selected collections
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


def CAP_Update_ProxyCol_RootObject(self, context):
    """
    Updates the "Root Object" property for all selected collections
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

def CAP_Update_ProxyCol_CollectionObjects(self, context):
    """
    Updates the "Child Objects" property for all selected collections
    """

    preferences = context.preferences
    addon_prefs = preferences.addons['Capsule'].preferences
    proxy = context.scene.CAPProxy
    
    # If updates are disabled, return early.
    if proxy.disable_updates == True:
        return

    collected = search_utils.GetEditableCollections(context)
    value = proxy.col_object_children

    # Run through the objects
    for collection in collected:
        collection.CAPCol.object_children = value

    return None


def CAP_Update_ProxyCol_CollectionChildren(self, context):
    """
    Updates the "Child Collections" property for all selected collections
    """

    preferences = context.preferences
    addon_prefs = preferences.addons['Capsule'].preferences
    proxy = context.scene.CAPProxy
    
    # If updates are disabled, return early.
    if proxy.disable_updates == True:
        return

    collected = search_utils.GetEditableCollections(context)
    value = proxy.col_collection_children

    # Run through the objects
    for collection in collected:
        collection.CAPCol.collection_children = value

    return None


def CAP_Update_ProxyCol_LocationPreset(self, context):
    """
    Updates the "Location Preset" property for all selected collections
    """
    preferences = context.preferences
    addon_prefs = preferences.addons['Capsule'].preferences
    proxy = context.scene.CAPProxy
    
    # If updates are disabled, return early.
    if proxy.disable_updates == True:
        return

    collected = search_utils.GetEditableCollections(context)
    value = proxy.col_location_preset

    # Run through the objects
    for collection in collected:
        collection.CAPCol.location_preset = value

    return None

def CAP_Update_ProxyCol_ExportPreset(self, context):
    """
    Updates the "Export Preset" property for all selected collections
    """
    preferences = context.preferences
    addon_prefs = preferences.addons['Capsule'].preferences
    proxy = context.scene.CAPProxy
    
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
    Updates the "Pack Script" property for all selected collections
    """
    preferences = context.preferences
    addon_prefs = preferences.addons['Capsule'].preferences
    proxy = context.scene.CAPProxy
    
    # If updates are disabled, return early.
    if proxy.disable_updates == True:
        return

    collected = search_utils.GetEditableCollections(context)
    value = proxy.col_pack_script

    # Run through the objects
    for collection in collected:
        collection.CAPCol.pack_script = value

    return None


