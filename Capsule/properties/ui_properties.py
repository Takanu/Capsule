
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
    CAP_Update_ProxyObjectExport, 
    CAP_Update_ProxyObjectOriginPoint, 
    CAP_Update_ProxyObjectLocationPreset, 
    CAP_Update_ProxyObjectExportPreset, 
)

from ..update.update_collections import (
    CAP_Update_ProxyCollectionExport, 
    CAP_Update_ProxyCollectionOriginPoint,
    CAP_Update_ProxyCollectionRootObject, 
    CAP_Update_ProxyCollectionChildExportOption,
    CAP_Update_ProxyCollectionLocationPreset, 
    CAP_Update_ProxyCollectionExportDefault, 
)

from bpy.types import PropertyGroup

def GetLocationPresets(scene, context):

    items = [
        ("0", "None",  "", 0),
        ]

    preferences = context.preferences
    addon_prefs = preferences.addons['Capsule'].preferences
    try:
        exp = bpy.data.objects[addon_prefs.default_datablock].CAPExp
    except KeyError:
        return items


    u = 1

    for i,x in enumerate(exp.location_presets):
        items.append((str(i+1), x.name, x.name, i+1))

    return items

def GetExportDefaults(scene, context):

    items = [
        ("0", "None",  "", 0),
        ]

    preferences = context.preferences
    addon_prefs = preferences.addons['Capsule'].preferences
    try:
        exp = bpy.data.objects[addon_prefs.default_datablock].CAPExp
    except KeyError:
        return items


    u = 1

    for i,x in enumerate(exp.export_presets):
        items.append((str(i+1), x.name, x.name, i+1))

    return items

class CAPSULE_Proxy_Properties(PropertyGroup):
    """
    A special property block that is held in the scene to manage selection editing and special multi-edit functionality.
    """

    disable_updates: BoolProperty(
        name = "(INTERNAL) Disable Updates",
        description = "Used by CheckSelectedObject to update the currently stored proxy properties without triggering update functions.",
        default = False,
        )

    obj_enable_export: BoolProperty(
        name = "Enable Export",
        description = "Enables or disables the ability to export this object.",
        default = False,
        update = CAP_Update_ProxyObjectExport
        )

    obj_origin_point: EnumProperty(
        name="Export Origin",
        description="Determines what the origin point of the exported file is set to.",
        items=(
        ('Object', 'Object', "Sets the exported origin point to the object's origin point."),
        ('Scene', 'Scene', "Keeps the exported origin point to the scene's origin point.")),
        update=CAP_Update_ProxyObjectOriginPoint
        )

    obj_location_preset: EnumProperty(
        name="Select Location Preset",
        description="Defines the file path that the object will be exported to.",
        items=GetLocationPresets,
        update=CAP_Update_ProxyObjectLocationPreset
        )

    obj_export_preset: EnumProperty(
        name="Select Export Preset",
        description="Defines the export settings used on the object.",
        items=GetExportDefaults,
        update=CAP_Update_ProxyObjectExportPreset
        )
    
    col_enable_export: BoolProperty(
        name="Export Collection",
        description="Enables or disables the ability to export this collection.",
        default=False,
        update=CAP_Update_ProxyCollectionExport
        )
    
    col_origin_point: EnumProperty(
        name="Export Origin",
        description="Determines what the origin point of the exported file is set to.",
        items=(
        ('Object', 'Object', "Sets the exported origin point to the origin point of a chosen object."),
        ('Scene', 'Scene', "Keeps the exported origin point to the scene's origin point.")),
        update=CAP_Update_ProxyCollectionOriginPoint,
        )
        
    col_root_object: StringProperty(
        name="Origin Object",
        description="Defines the origin point of the exported collection object.",
        default="",
        update=CAP_Update_ProxyCollectionRootObject,
        )

    col_child_export_option: EnumProperty(
        name="Child Export Options",
        description="Lets you set how children of a collection are included in the export.",
        items=(
        ('All', 'All Children', "Will export the children of this collection as well as every object associated to a child of this collection."),
        ('Immediate', 'Immediate Children Only', "Will only export objects that are a child of this collection."),
        ('Down 1', 'One Layer Down', "Will export all children up to one layer down the hierarchy tree."),
        ('Down 2', 'Two Layers Down', "Will export all children up to two layers down the hierarchy tree."),
        ('Down 3', 'Three Layers Down', "Will export all children up to three layers down the hierarchy tree."),
        ('Down 4', 'Four Layers Down', "Will export all children up to four layers down the hierarchy tree."),
        ('Down 5', 'Five Layer Down', "Will export all children up to five layers down the hierarchy tree.")
        ),
        update=CAP_Update_ProxyCollectionChildExportOption,
        )

    col_location_preset: EnumProperty(
        name="Select Export Location",
        description="Defines the Location that the collection will be exported to.",
        items=GetLocationPresets,
        update=CAP_Update_ProxyCollectionLocationPreset,
        )

    col_export_preset: EnumProperty(
        name="Select Export Default",
        description="Defines the export settings used on the collection.",
        items=GetExportDefaults,
        update=CAP_Update_ProxyCollectionExportDefault
        )