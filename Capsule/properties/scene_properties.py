
import bpy
from bpy.props import IntProperty, BoolProperty, FloatProperty, EnumProperty, PointerProperty, StringProperty, CollectionProperty
from bpy.types import PropertyGroup

from ..update.update_objects import (
    CAP_Update_ObjectListName, 
    CAP_Update_ObjectListExport, 
    CAP_Update_ActionItemName, 
    CAP_Update_FocusObject,  
    CAP_Update_SelectObject, 
    CAP_Update_ObjectListRemove
)

from ..update.update_collections import (
    CAP_Update_CollectionListName, 
    CAP_Update_CollectionListExport, 
    CAP_Update_FocusCollection, 
    CAP_Update_SelectCollection, 
    CAP_Update_CollectionListRemove
)

from ..tk_utils.collections import GetSelectedObjectCollections

class ObjectListItem(PropertyGroup):
    """
    Defines an object as a list property, for use when displaying objects in the user interface.
    """
    name: StringProperty(
        name="",
        description="The name of the object.",
        update=CAP_Update_ObjectListName
        )

    prev_name: StringProperty(
        name="",
        description="Internal only, used for tracking name updates."
        )

    enable_export: BoolProperty(
        name="",
        description="Enables or disables the ability to export this object.",
        default=False,
        update=CAP_Update_ObjectListExport
        )

    sel: BoolProperty(
        name="Select",
        description="Selects the object in the scene",
        default=True,
        update=CAP_Update_SelectObject
        )

    focus: BoolProperty(
        name="Focus",
        description="Focuses the camera to the object",
        default=True,
        update=CAP_Update_FocusObject
        )

    remove: BoolProperty(
        name="",
        description="Removes the object from the list, and un-marks it for export.",
        default=True,
        update=CAP_Update_ObjectListRemove
        )

class CollectionListItem(PropertyGroup):
    """
    Defines a collection as a list property, for use when displaying collections in the user interface.
    """
    name: StringProperty(
        name="",
        description="The name of the collection.",
        update=CAP_Update_CollectionListName
        )

    prev_name: StringProperty(
        name="",
        description="Internal only, used for tracking name updates."
        )

    enable_export: BoolProperty(
        name="",
        description="Enables or disables the ability to export this collection.",
        default=False,
        update=CAP_Update_CollectionListExport
        )
    
    sel: BoolProperty(
        name="Select",
        description="Selects the collection in the scene",
        default=True,
        update=CAP_Update_SelectCollection
        )

    focus: BoolProperty(
        name="Focus Export",
        description="Focuses the camera to the entire collection.",
        default=True,
        update=CAP_Update_FocusCollection
        )

    remove: BoolProperty(
        name="",
        description="Removes the collection from the list, and un-marks it for export.",
        default=True,
        update=CAP_Update_CollectionListRemove
        )

class ActionListItem(PropertyGroup):
    """
    Defines an animation action as a list property, for use when displaying actions in the user interface.
    """
    name: StringProperty(
        name="",
        description="The name of the action.",
        update=CAP_Update_ActionItemName
        )

    prev_name: StringProperty(
        name="",
        description="Internal only, used for tracking name updates."
        )

    anim_type: EnumProperty(
        name="Animation Data Type",
        description="Switches the selection editing mode between individual, selected objects and collections that can be browsed and edited through a list.",
        items=(
        ('1', 'Action Object', ''),
        ('2', 'NLA Object', ''),
        ('3', 'Action Armature', ''),
        ('4', 'NLA Armature', ''),),
        )

def GetSelectedCollections(scene, context):

    items = [
        ("0", "None",  "", 0),
        ]

    scn = context.scene.CAPScn
    scn.collection_selected_list.clear()
    u = 1

    for i,x in enumerate(GetSelectedObjectCollections()):
        items.append((str(i+1), x.name, x.name, i+1))
        new_collection_entry = scn.collection_selected_list.add()
        new_collection_entry.name = x.name

    return items

class CAPSULE_Scene_Preferences(PropertyGroup):
    """
    A random assortment of scene-specific properties with some "weird" toggle stuff.
    """

    # A collection that stores the list of collections that Capsule is currently displaying in the UI list.
    collection_list: CollectionProperty(type=CollectionListItem)

    # ???
    collection_list_index: IntProperty(
        name="",
        description="",
        )

    ## ???
    collection_selected_list: CollectionProperty(type=CollectionListItem)

    ## ???
    collection_selected_list_enum: EnumProperty(items=GetSelectedCollections)

    ## The index of the currently selected collection from the UI list.  Will be -1 if not selected.
    collection_selected_list_index: IntProperty()

    # A collection that stores the list of objects that Capsule is currently displaying in the UI list.
    object_list: CollectionProperty(type=ObjectListItem)

    # ???
    object_list_index: IntProperty(name="",
        description="",
        )

    ## Old Action list variables
    action_list: CollectionProperty(type=ActionListItem)
    action_list_index: IntProperty()

    list_switch: EnumProperty(
        name="Object Type Switch",
        description="Switches the list display mode between objects and collections.",
        items=(
        ('1', 'Objects', 'Displays the Export List for objects in the currently visible scene.'),
        ('2', 'Collections', 'Displays the Export List for collections in the currently visible scene')),
        )

    selection_switch: EnumProperty(
        name="Selection Switch",
        description="Switches the selection editing mode between objects and collections.",
        items=(
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

class CAPSULE_Object_Preferences(PropertyGroup):
    """
    A special property block that all objects receive when Capsule is registered, allowing it to store
    required information to manage it as a potential export target.
    """

    enable_export: BoolProperty(
        name = "Enable Export",
        description = "Enables or disables the ability to export this object.",
        default = False,
        )

    origin_point: EnumProperty(
        name="Export Origin",
        description="Determines what the origin point of the exported file is set to.",
        items=(
        ('Object', 'Object', "Sets the exported origin point to the object's origin point."),
        ('Scene', 'Scene', "Keeps the exported origin point to the scene's origin point.")),
        )

    # use_scene_origin: BoolProperty(
    #     name="Use Scene Origin",
    #     description="If turned on, the scene's centre will be used as an origin point for the exported object, rather than the object's own origin point.  \n\nIf you have a complex object with many constraints and modifiers and it's not exporting properly without this feature, use this feature <3",
    #     default=False,
    #     )

    location_preset: EnumProperty(
        name="Select Location Preset",
        description="Defines the file path that the object will be exported to.",
        items=GetLocationPresets,
        )

    export_preset: EnumProperty(
        name="Select Export Preset",
        description="Defines the export settings used on the object.",
        items=GetExportDefaults,
        )

    enable_edit: BoolProperty(
        name="",
        description="Enables editing of the object's properties when selected.",
    )

    in_export_list: BoolProperty(
        name="",
        description="(Internal Only) Prevents refreshes of the Export List from removing items not marked for export.",
        default=False
        )

class CAPSULE_Collection_Preferences(PropertyGroup):
    """
    A special property block that all collections receive when Capsule is registered, allowing it to store
    required information to manage it as a potential export target.
    """
    enable_export: BoolProperty(
        name="Export Collection",
        description="Enables or disables the ability to export this collection.",
        default=False,
        )
    
    origin_point: EnumProperty(
        name="Export Origin",
        description="Determines what the origin point of the exported file is set to.",
        items=(
        ('Object', 'Object', "Sets the exported origin point to the origin point of a chosen object."),
        ('Scene', 'Scene', "Keeps the exported origin point to the scene's origin point.")),
        )

    root_object: StringProperty(
        name="Origin Object",
        description="Defines what object will be used as the exported collection's origin point.",
        default="",
        )
    
    child_export_option: EnumProperty(
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
        )

    location_preset: EnumProperty(
        name="Select Export Location",
        description="Defines the Location that the collection will be exported to.",
        items=GetLocationPresets,
        )

    export_preset: EnumProperty(
        name="Select Export Default",
        description="Defines the export settings used on the collection.",
        items=GetExportDefaults,
        )
    
    export_preset: EnumProperty(
        name="Select Export Default",
        description="Defines the export settings used on the collection.",
        items=GetExportDefaults,
        )
    
    enable_edit: BoolProperty(
        name="",
        description="Enables editing of the collection's properties.",
    )

    in_export_list: BoolProperty(
        name="",
        description="(Internal Only) Prevents refreshes of the Export List from removing items not marked for export.",
        default=False
        )

def GetExportPresets(scene, context):

    items = []
    preferences = context.preferences
    addon_prefs = preferences.addons["Blinkey"].preferences

    u = 1

    for i,x in enumerate(addon_prefs.presets):
        items.append((str(i), x.name, x.name, i))

    return items

class CAPSULE_Object_StateMachine(PropertyGroup):

    has_triangulate: BoolProperty(
        name="Has Triangulation Modifier",
        description="Internal variable used to monitor whether or not the object has a Triangulation modifier, when triangulating the mesh ",
        default=False
        )

class CAPSULE_Action_Preferences(PropertyGroup):
    export: BoolProperty(
        name="Export",
        description="Determines whether the action can be exported or not.",
        default=True
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
#     CAPSULE_Object_StateMachine, 
#     # CAPSULE_Action_Preferences
# )

# def register():
#     print("~~~Registering Generic Properties~~~")
#     for cls in classes:
#         bpy.utils.register_class(cls)


# def unregister():
#     print("~~~Un-registering Generic Properties~~~")
#     for cls in reversed(classes):
#         bpy.utils.unregister_class(cls)

