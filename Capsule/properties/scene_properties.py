
import bpy
from bpy.props import IntProperty, BoolProperty, FloatProperty, EnumProperty, PointerProperty, StringProperty, CollectionProperty
from bpy.types import PropertyGroup

from ..update.update_objects import (
    CAP_Update_ObjectListExport, 
    CAP_Update_ActionItemName, 
    CAP_Update_FocusObject,  
    CAP_Update_SelectObject, 
    CAP_Update_ObjectListRemove
)

from ..update.update_collections import (
    CAP_Update_CollectionListExport, 
    CAP_Update_FocusCollection, 
    CAP_Update_SelectCollection, 
    CAP_Update_CollectionListRemove
)

from ..tk_utils.search import GetSelectedCollections

class ObjectListItem(PropertyGroup):
    """
    Defines an object as a list property, for use when displaying objects in the user interface.
    """

    #URGENT: This needs an update property!
    object: PointerProperty(
        type = bpy.types.Object,
        name = "Object",
        description = "A pointer for the object this list item represents",
    )

    enable_export: BoolProperty(
        name = "",
        description = "Enables or disables the ability to export this object",
        default = False,
        update = CAP_Update_ObjectListExport
    )

    # Secondary functions
    sel: BoolProperty(
        name = "Select",
        description = "Selects the object in the scene",
        default = True,
        update = CAP_Update_SelectObject
    )

    focus: BoolProperty(
        name = "Focus",
        description = "Focuses the camera to the object",
        default = True,
        update = CAP_Update_FocusObject
    )

    remove: BoolProperty(
        name = "",
        description = "Removes the object from the list, and un-marks it for export",
        default = True,
        update = CAP_Update_ObjectListRemove
    )
    
    # this value exists purely to display a label with correct padding in a UIList
    # no longer needed for now, keeping here just in case
    # deleted_name: StringProperty(
    #     name = "Deleted Object",
    #     description = "This object has been deleted from the Scene",
    #     default = "Deleted Object",
    # )

    # this value exists purely to enable the display of a tooltip, this property does nothing otherwise
    missing_data: BoolProperty(
        name = "",
        description = "This export has missing data that will prevent it from being exported.  Make sure all export options are set",
        default = True,
    )

class CollectionListItem(PropertyGroup):
    """
    Defines a collection as a list property, for use when displaying collections in the user interface.
    """
    collection: PointerProperty(
        type = bpy.types.Collection,
        name = "Collection",
        description = "The collection data this list entry represents",
    )

    prev_name: StringProperty(
        name = "",
        description = "Internal only, used for tracking name updates"
    )

    enable_export: BoolProperty(
        name = "",
        description = "Enables or disables the ability to export this collection",
        default = False,
        update = CAP_Update_CollectionListExport
    )
    
    sel: BoolProperty(
        name = "Select",
        description = "Selects the collection in the scene",
        default = True,
        update = CAP_Update_SelectCollection
    )

    focus: BoolProperty(
        name = "Focus Export",
        description = "Focuses the camera to the entire collection (if there's an object in the collection that is selectable)",
        default = True,
        update = CAP_Update_FocusCollection
    )

    remove: BoolProperty(
        name = "",
        description = "Removes the collection from the list, and un-marks it for export",
        default = True,
        update = CAP_Update_CollectionListRemove
    )

    # this value exists purely to display a label with correct padding in a UIList
    # no longer needed for now, keeping here just in case    
    # deleted_name: StringProperty(
    #     name = "Deleted Collection",
    #     description = "Used by lists to show that the collection being accessed has been deleted",
    #     default = "Deleted Collection",
    # )

    # this value exists purely to enable the display of a tooltip, this property does nothing otherwise
    missing_data: BoolProperty(
        name = "",
        description = "This export has missing data that will prevent it from being exported.  Make sure all export options are set",
        default = True,
    )

class ActionListItem(PropertyGroup):
    """
    Defines an animation action as a list property, for use when displaying actions in the user interface.
    """
    name: StringProperty(
        name = "",
        description = "The name of the action",
        update = CAP_Update_ActionItemName
    )

    prev_name: StringProperty(
        name = "",
        description = "Internal only, used for tracking name updates"
    )

    anim_type: EnumProperty(
        name = "Animation Data Type",
        description = "Switches the selection editing mode between individual, selected objects and collections that can be browsed and edited through a list",
        items =  (
        ('1', 'Action Object', ''),
        ('2', 'NLA Object', ''),
        ('3', 'Action Armature', ''),
        ('4', 'NLA Armature', ''),),
    )


class CAPSULE_Scene_Preferences(PropertyGroup):
    """
    A random assortment of scene-specific properties with some "weird" toggle stuff.
    """

    # A collection that stores the list of objects that Capsule is currently displaying in the UI list.
    object_list: CollectionProperty(type=ObjectListItem)

    # The index of the selected object list item
    object_list_index: IntProperty()

    # A collection that stores the list of collections that Capsule is currently displaying in the UI list.
    collection_list: CollectionProperty(type=CollectionListItem)

    # The index of the selected collection list item
    collection_list_index: IntProperty()


    ## Old Action list variables
    action_list: CollectionProperty(type=ActionListItem)
    action_list_index: IntProperty()

    list_switch: EnumProperty(
        name = "Object Type Switch",
        description = "Switches the list display mode between objects and collections",
        items =  (
        ('1', 'Objects', 'Displays the Export List for objects in the currently visible scene.'),
        ('2', 'Collections', 'Displays the Export List for collections in the currently visible scene')),
    )

    selection_switch: EnumProperty(
        name = "Selection Switch",
        description = "Switches the selection editing mode between objects and collections",
        items =  (
        ('1', 'Objects', 'Displays selected objects, and any associated export settings.'),
        ('2', 'Collections', 'Displays selected collections, and any associated export settings.')),
    )

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

class CAPSULE_Object_Preferences(PropertyGroup):
    """
    A special property block that all objects receive when Capsule is registered, allowing it to store
    required information to manage it as a potential export target.
    """

    enable_export: BoolProperty(
        name = "Enable Export",
        description = "Enables or disables the ability to export this object",
        default = False,
    )

    origin_point: EnumProperty(
        name = "Origin Export",
        description = "Determines what the origin point of the exported file is set to",
        items =  (
        ('Object', 'Object', "Sets the exported origin point to the object's origin point"),
        ('Scene', 'Scene', "Keeps the exported origin point to the scene's origin point")),
    )

    location_preset: EnumProperty(
        name = "File Location",
        description = "Defines the file path that the object will be exported to",
        items = GetLocationPresets,
    )

    export_preset: EnumProperty(
        name = "Export Preset",
        description = "Defines the export settings used on the object",
        items = GetExportDefaults,
    )

    override: PointerProperty(
        type = bpy.types.Text,
        name = "Override",
        description = "Defines a python script that will be executed just before and after Capsule exports the object to a file, after it has prepared everything in the scene.  Check the Capsule GitHub Wiki for more information on how to use this feature",
    )

    enable_edit: BoolProperty(
        name = "",
        description = "Enables editing of the object's properties when selected",
    )

    in_export_list: BoolProperty(
        name = "",
        description = "(Internal Only) Prevents refreshes of the Export List from removing items not marked for export",
        default = False
    )

class CAPSULE_Collection_Preferences(PropertyGroup):
    """
    A special property block that all collections receive when Capsule is registered, allowing it to store
    required information to manage it as a potential export target.
    """
    enable_export: BoolProperty(
        name = "Export Collection",
        description = "Enables or disables the ability to export this collection",
        default = False,
    )
    
    origin_point: EnumProperty(
        name = "Origin Export",
        description = "Determines what the origin point of the exported file is set to",
        items =  (
        ('Object', 'Object', "Sets the exported origin point to the origin point of a chosen object"),
        ('Scene', 'Scene', "Keeps the exported origin point to the scene's origin point")),
    )

    root_object: PointerProperty(
        type = bpy.types.Object,
        name = "Origin Object",
        description = "Defines what object will be used as the exported collection's origin point",
    )
    
    child_export_option: EnumProperty(
        name = "Hierarchy",
        description = "Lets you set how children of a collection are included in the export",
        items =  (
        ('All', 'All Children', "Will export the children of this collection as well as every object associated to a child of this collection"),
        ('Immediate', 'Immediate Children Only', "Will only export objects that are a child of this collection"),
        ('Down 1', 'One Layer Down', "Will export all children up to one layer down the hierarchy tree"),
        ('Down 2', 'Two Layers Down', "Will export all children up to two layers down the hierarchy tree"),
        ('Down 3', 'Three Layers Down', "Will export all children up to three layers down the hierarchy tree"),
        ('Down 4', 'Four Layers Down', "Will export all children up to four layers down the hierarchy tree"),
        ('Down 5', 'Five Layer Down', "Will export all children up to five layers down the hierarchy tree")
        ),
    )

    location_preset: EnumProperty(
        name = "File Location",
        description = "Defines the Location that the collection will be exported to",
        items = GetLocationPresets,
    )

    export_preset: EnumProperty(
        name = "Export Preset",
        description = "Defines the export settings used on the collection",
        items = GetExportDefaults,
    )
    
    override: PointerProperty(
        type = bpy.types.Text,
        name = "Override",
        description = "Defines a python script that will be executed just before and after Capsule exports to a file, after it has prepared everything in the scene.  Check the Capsule GitHub Wiki for more information on how to use this feature",
    )
    
    enable_edit: BoolProperty(
        name = "",
        description = "Enables editing of the collection's properties",
    )

    in_export_list: BoolProperty(
        name = "",
        description = "(Internal Only) Prevents refreshes of the Export List from removing items not marked for export",
        default = False
    )

class CAPSULE_Export_Status(PropertyGroup):
    """
    A property group used to externalize the current status of a Capsule Export Operator.  This is specifically
    being used for the Override feature
    """

    target_name: StringProperty(
        name = "Export Target Name",
        description = "The name of the Export Target that Capsule is currently performing operations on.  This will be the name of an Object or Collection",
        default = "",
    )

    target_type: EnumProperty(
        name = "Export Target Type",
        description = "Indicates whether the current Export Target is an Object or Collection",
        items =  (
        ('OBJECT', 'Object', "Capsule has performed all preparation actions and is about to export the current Export Target"),
        ('COLLECTION', 'Collection', "Capsule has just exported the Export Target and is about to perform clean-up operations"),
        ),
    )

    target_status: EnumProperty(
        name = "Export Status",
        description = "Describes what stage of the export process Capsule is at for the current target",
        items =  (
        ('NONE', 'None', "Capsule is currently inactive"),
        ('BEFORE_EXPORT', 'Before Export', "Capsule has performed all preparation actions and is about to export the current Export Target"),
        ('AFTER_EXPORT', 'After Export', "Capsule has just exported the Export Target and is about to perform clean-up operations"),
        ),
        default = 'NONE',
    )




# ////////////////////// - CLASS REGISTRATION - ////////////////////////
# decided to do it all in __init__ instead, skipping for now.

# classes = (
#     ObjectListItem, 
#     CollectionListItem, 
#     ActionListItem, 
#     CAPSULE_Scene_Preferences, 
#     CAPSULE_Object_Preferences, 
#     CAPSULE_Collection_Preferences, 
# )

# def register():
#     #print("~~~Registering Generic Properties~~~")
#     for cls in classes:
#         bpy.utils.register_class(cls)


# def unregister():
#     #print("~~~Un-registering Generic Properties~~~")
#     for cls in reversed(classes):
#         bpy.utils.unregister_class(cls)

