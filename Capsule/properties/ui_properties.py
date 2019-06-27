
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
    CAP_Update_ObjectExport, 
    CAP_Update_SceneOrigin, 
    CAP_Update_LocationPreset, 
    CAP_Update_ExportDefault, 
)

from ..update.update_collections import (
    CAP_Update_CollectionExport, 
    CAP_Update_CollectionRootObject, 
    CAP_Update_CollectionLocationPreset, 
    CAP_Update_CollectionExportDefault, 
)

from bpy.types import PropertyGroup

def GetLocationPresets(scene, context):

    items = [
        ("0", "None",  "", 0),
        ]

    preferences = context.preferences
    addon_prefs = preferences.addons['Capsule'].preferences
    exp = bpy.data.objects[addon_prefs.default_datablock].CAPExp

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
    exp = bpy.data.objects[addon_prefs.default_datablock].CAPExp

    u = 1

    for i,x in enumerate(exp.file_presets):
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
        update = CAP_Update_ObjectExport
        )

    obj_use_scene_origin: BoolProperty(
        name="Use Scene Origin",
        description="If turned on, the scene's centre will be used as an origin point for the exported object, rather than the object's own origin point.  \n\nIf you have a complex object with many constraints and modifiers and it's not exporting properly without this feature, use this feature <3",
        default=False,
        update=CAP_Update_SceneOrigin
        )

    obj_location_preset: EnumProperty(
        name="Select Location Preset",
        description="Defines the file path that the object will be exported to.",
        items=GetLocationPresets,
        update=CAP_Update_LocationPreset
        )

    obj_export_preset: EnumProperty(
        name="Select Export Preset",
        description="Defines the export settings used on the object.",
        items=GetExportDefaults,
        update=CAP_Update_ExportDefault
        )
    
    col_enable_export: BoolProperty(
        name="Export Collection",
        description="Enables or disables the ability to export this collection.",
        default=False,
        update=CAP_Update_CollectionExport
        )

    col_root_object: StringProperty(
        name="Origin Object",
        description="Defines the origin point of the exported collection object.  If not defined, the origin will be the scene's origin point.  \n\nIf you have a complex object with many constraints and modifiers and it's not exporting properly with a defined root object, leave it blank <3",
        default="",
        update=CAP_Update_CollectionRootObject
        )

    col_location_preset: EnumProperty(
        name="Select Export Location",
        description="Defines the Location that the collection will be exported to.",
        items=GetLocationPresets,
        update=CAP_Update_CollectionLocationPreset,
        )

    col_export_preset: EnumProperty(
        name="Select Export Default",
        description="Defines the export settings used on the collection.",
        items=GetExportDefaults,
        update=CAP_Update_CollectionExportDefault
        )