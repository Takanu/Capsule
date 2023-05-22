
import bpy
from bpy.props import (
    IntProperty, 
    BoolProperty, 
    FloatProperty, 
    EnumProperty, 
    PointerProperty, 
    StringProperty, 
    CollectionProperty,
)

from ..update.update_objects import (
    CAP_Update_ProxyObj_EnableExport, 
    CAP_Update_ProxyObj_OriginPoint, 
    CAP_Update_ProxyObj_ObjectChildren,
    CAP_Update_ProxyObj_LocationPreset, 
    CAP_Update_ProxyObj_ExportPreset, 
    CAP_Update_ProxyObj_PackScript,
)

from ..update.update_collections import (
    CAP_Update_ProxyCol_EnableExport, 
    CAP_Update_ProxyCol_OriginPoint,
    CAP_Update_ProxyCol_RootObject, 
    CAP_Update_ProxyCol_CollectionObjects,
    CAP_Update_ProxyCol_CollectionChildren,
    CAP_Update_ProxyCol_LocationPreset, 
    CAP_Update_ProxyCol_ExportPreset, 
    CAP_Update_ProxyCollectionOverride,
)

from bpy.types import PropertyGroup

def GetLocationPresets(scene, context):

    items = [
        ("0", "None",  "", 0),
        ]

    preferences = context.preferences
    addon_prefs = preferences.addons['Capsule'].preferences
    try:
        cap_file = bpy.data.objects[addon_prefs.default_datablock].CAPFile
    except KeyError:
        return items


    u = 1

    for i,x in enumerate(cap_file.location_presets):
        items.append((str(i+1), x.name, x.name, i+1))

    return items

def GetExportDefaults(scene, context):

    items = [
        ("0", "None",  "", 0),
        ]

    preferences = context.preferences
    addon_prefs = preferences.addons['Capsule'].preferences
    try:
        cap_file = bpy.data.objects[addon_prefs.default_datablock].CAPFile
    except KeyError:
        return items


    u = 1

    for i,x in enumerate(cap_file.export_presets):
        items.append((str(i+1), x.name, x.name, i+1))

    return items

class CAPSULE_Proxy_Properties(PropertyGroup):
    """
    A special property block that is held in the scene to manage selection editing and special multi-edit functionality.
    """

    # TODO: Ensure this works properly with the new Collection selection code.
    disable_updates: BoolProperty(
        name = "(INTERNAL) Disable Updates",
        description = "Used by CheckSelectedObject to update the currently stored proxy properties without triggering update functions.",
        default = False,
    )

    # ////////////
    # OBJECT

    obj_enable_export: BoolProperty(
        name = "Enable Export",
        description = "Enable or disable exports of this Object using Capsule",
        default = False,
        update = CAP_Update_ProxyObj_EnableExport
    )

    obj_origin_point: EnumProperty(
        name = "Origin Export",
        description = "Determine the location of the origin point upon export",
        items =  (
        ('Object', 'Object', "Set the exported origin point to the object's origin point"),
        ('Scene', 'Scene', "Keep the exported origin point to the scene's origin point")),
        update = CAP_Update_ProxyObj_OriginPoint
    )

    obj_object_children: EnumProperty(
        name = "Child Objects",
        description = "Set how children of an object are included in the export",
        items =  (
        ('All', 'All', "Will export all children of this object"),
        ('None', 'None', "No object children will be exported"),
        ('Down 1', 'One Layer Down', "Will export all children up to one layer down the object hierarchy"),
        ('Down 2', 'Two Layers Down', "Will export all children up to two layers down the object hierarchy"),
        ('Down 3', 'Three Layers Down', "Will export all children up to three layers down the object hierarchy"),
        ('Down 4', 'Four Layers Down', "Will export all children up to four layers down the object hierarchy"),
        ('Down 5', 'Five Layers Down', "Will export all children up to five layers down the object hierarchy")
        ),
        update = CAP_Update_ProxyObj_ObjectChildren,
    )

    obj_location_preset: EnumProperty(
        name = "Export Location",
        description = "Select the file path that the object will be exported to",
        items = GetLocationPresets,
        update = CAP_Update_ProxyObj_LocationPreset
    )

    obj_export_preset: EnumProperty(
        name = "Export Preset",
        description = "Select the Export Preset used to export this object",
        items = GetExportDefaults,
        update = CAP_Update_ProxyObj_ExportPreset
    )

    obj_pack_script: PointerProperty(
        type = bpy.types.Text,
        name = "Pack Script",
        description = "(Optional) Define a python script that will be executed just before and after Capsule exports the object to a file, after it has prepared everything in the scene.  Check the Capsule GitHub Wiki for more information on how to use this feature",
        update = CAP_Update_ProxyObj_PackScript,
    )
    
    # ////////////
    # COLLECTION
    
    col_enable_export: BoolProperty(
        name = "Export Collection",
        description = "Enable or disable exports of this Collection using Capsule",
        default = False,
        update = CAP_Update_ProxyCol_EnableExport
    )
    
    col_origin_point: EnumProperty(
        name = "Origin Export",
        description = "Determine the location of the origin point upon export",
        items =  (
        ('Object', 'Object', "Set the exported origin point to the origin point of a chosen object"),
        ('Scene', 'Scene', "Keep the exported origin point to the scene's origin point")),
        update = CAP_Update_ProxyCol_OriginPoint,
    )
        
    col_root_object: PointerProperty(
        type = bpy.types.Object,
        name = "Origin Object",
        description = "Define the origin point of the exported collection object",
        update = CAP_Update_ProxyCol_RootObject,
    )

    # NOTE: Currently not used due to extra complexities in searching for children within collections.
    col_object_children: EnumProperty(
        name = "Child Objects",
        description = "Set how children of an exportable object are included in the export.  This includes any objects found from the children of collections inside this collection",
        items =  (
        ('All', 'All', "Will export all children of an exportable object"),
        ('None', 'None', "No object children will be exported"),
        ('Down 1', 'One Layer Down', "Will export all children up to one layer down the object hierarchy"),
        ('Down 2', 'Two Layers Down', "Will export all children up to two layers down the object hierarchy"),
        ('Down 3', 'Three Layers Down', "Will export all children up to three layers down the object hierarchy"),
        ('Down 4', 'Four Layers Down', "Will export all children up to four layers down the object hierarchy"),
        ('Down 5', 'Five Layers Down', "Will export all children up to five layers down the object hierarchy")
        ),
        update = CAP_Update_ProxyCol_CollectionObjects,
    )

    col_collection_children: EnumProperty(
        name = "Child Collections",
        description = "Set how children of a collection are included in the export",
        items =  (
        ('All', 'All', "Will export the children of this collection as well as every object associated to a child of this collection."),
        ('None', 'None', "Will only export objects that are a child of this collection."),
        ('Down 1', 'One Layer Down', "Will export all children up to one layer down the collection hierarchy"),
        ('Down 2', 'Two Layers Down', "Will export all children up to two layers down the collection hierarchy"),
        ('Down 3', 'Three Layers Down', "Will export all children up to three layers down the collection hierarchy"),
        ('Down 4', 'Four Layers Down', "Will export all children up to four layers down the collection hierarchy"),
        ('Down 5', 'Five Layers Down', "Will export all children up to five layers down the collection hierarchy")
        ),
        update = CAP_Update_ProxyCol_CollectionChildren,
    )

    col_location_preset: EnumProperty(
        name = "Export Location",
        description = "Select the file path that the collection will be exported to",
        items = GetLocationPresets,
        update = CAP_Update_ProxyCol_LocationPreset,
    )

    col_export_preset: EnumProperty(
        name = "Export Preset",
        description = "Select the Export Preset used to export this collection",
        items = GetExportDefaults,
        update = CAP_Update_ProxyCol_ExportPreset
    )

    col_pack_script: PointerProperty(
        type = bpy.types.Text,
        name = "Pack Script",
        description = "(Optional) Define a python script that will be executed just before and after Capsule exports the collection to a file, after it has prepared everything in the scene.  Check the Capsule GitHub Wiki for more information on how to use this feature",
        update = CAP_Update_ProxyCollectionOverride,
    )