
import bpy, bmesh, time
from math import *

from .update_list import UpdateObjectList

# OBJECT DATA PROXY PROPERTIES
# /////////////////////////////////////////////////
# /////////////////////////////////////////////////

def FindEditableObjects(context):
    """
    Finds objects that can have their values edited.
    """
    collected = [] 
    active_obj = context.active_object

    # TODO: When I am able to fetch selected Outliner entries, remove the
    # reliance on selected objects.

    for item in context.selected_objects:
        if item.CAPObj.enable_edit is True:
            collected.append(item)
    
    # This is to ensure some parity with the Outliner.
    if active_obj.CAPObj.enable_edit is True:
        if active_obj not in collected:
            collected.append(active_obj)

    return collected

def CAP_Update_ProxyObj_EnableExport(self, context):
    """
    Updates the "Enable Export" property for all selected objects
    Note - This should only be used from the Enable Export UI tick, otherwise manually handle "Enable Export" status 
    assignment using "UpdateObjectList"
    """

    preferences = context.preferences
    addon_prefs = preferences.addons['Capsule'].preferences
    proxy = context.scene.CAPProxy

    # If updates are disabled, return early.
    if proxy.disable_updates == True:
        return

    # Setup initial targets and the value state we need to change.
    collected = FindEditableObjects(context)
    value = proxy.obj_enable_export

    # Run through any collected objects to also update them.
    for item in collected:
        item.CAPObj.enable_export = value
        UpdateObjectList(context.scene, item, value)


    return None


def CAP_Update_ProxyObj_OriginPoint(self, context):
    """
    Updates the "Origin Export" property for all selected objects.
    """
    preferences = context.preferences
    addon_prefs = preferences.addons['Capsule'].preferences
    proxy = context.scene.CAPProxy
    
    # If updates are disabled, return early.
    if proxy.disable_updates == True:
        return

    # Setup initial targets and the value state we need to change.
    collected = FindEditableObjects(context)
    value = proxy.obj_origin_point

    # Run through the objects
    for item in collected:
        item.CAPObj.origin_point = value

    return None

def CAP_Update_ProxyObj_ObjectChildren(self, context):
    """
    Updates the "Child Objects" property for all selected objects
    """
    preferences = context.preferences
    addon_prefs = preferences.addons['Capsule'].preferences
    proxy = context.scene.CAPProxy
    
    # If updates are disabled, return early.
    if proxy.disable_updates == True:
        return

    # Setup initial targets and the value state we need to change.
    collected = FindEditableObjects(context)
    value = proxy.obj_object_children

    # Run through the objects
    for item in collected:
        item.CAPObj.object_children = value

    return None


def  CAP_Update_ProxyObj_LocationPreset(self, context):
    """
    Updates the "Location Preset" property for all selected objects
    """

    preferences = context.preferences
    addon_prefs = preferences.addons['Capsule'].preferences
    proxy = context.scene.CAPProxy

    # If updates are disabled, return early.
    if proxy.disable_updates == True:
        return

    # Setup initial targets and the value state we need to change.
    collected = FindEditableObjects(context)
    value = proxy.obj_location_preset

    # Run through the objects
    for item in collected:
        item.CAPObj.location_preset = value

    return None

def CAP_Update_ProxyObj_ExportPreset(self, context):
    """
    Updates the "Export Preset" property for all selected objects
    """
    preferences = context.preferences
    addon_prefs = preferences.addons['Capsule'].preferences
    proxy = context.scene.CAPProxy
    
     # If updates are disabled, return early.
    if proxy.disable_updates == True:
        return

    # Setup initial targets and the value state we need to change.
    collected = FindEditableObjects(context)
    value = proxy.obj_export_preset

    # Run through the objects
    for item in collected:
        item.CAPObj.export_preset = value

    return None

def CAP_Update_ProxyObj_PackScript(self, context):
    """
    Updates the "Pack Script" property for all selected objects
    """
    preferences = context.preferences
    addon_prefs = preferences.addons['Capsule'].preferences
    proxy = context.scene.CAPProxy
    
     # If updates are disabled, return early.
    if proxy.disable_updates == True:
        return

    # Setup initial targets and the value state we need to change.
    collected = FindEditableObjects(context)
    print(collected)
    value = proxy.obj_pack_script

    # Run through the objects
    for item in collected:
        item.CAPObj.pack_script = value

    return None



