
import bpy
from bpy.props import IntProperty, BoolProperty, FloatProperty, EnumProperty, PointerProperty, StringProperty, CollectionProperty
from bpy.types import PropertyGroup

from .update import (
    CAP_Update_ObjectExport, 
    CAP_Update_SceneOrigin, 
    CAP_Update_LocationDefault, 
    CAP_Update_ExportDefault, 
    CAP_Update_Normals, 
    CAP_Update_ObjectListName, 
    CAP_Update_ObjectListExport, 
    CAP_Update_ActionItemName, 
    CAP_Update_FocusObject,  
    CAP_Update_SelectObject, 
    CAP_Update_ObjectListSelect, 
    CAP_Update_ObjectRemoveFromList
)

from .update_collections import (
    CAP_Update_CollectionListName, 
    CAP_Update_CollectionListExport, 
    CAP_Update_FocusCollection, 
    CAP_Update_SelectCollection, 
    CAP_Update_CollectionExport,
    CAP_Update_CollectionRootObject, 
    CAP_Update_CollectionExportDefault, 
    CAP_Update_CollectionLocationDefault, 
    CAP_Update_CollectionNormals, 
    CAP_Update_CollectionListSelect, 
    CAP_Update_CollectionRemoveFromList
)

from .tk_utils import collections as collection_utils

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
        update=CAP_Update_ObjectRemoveFromList
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
        update=CAP_Update_CollectionRemoveFromList
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

    for i,x in enumerate(collection_utils.GetSelectedObjectCollections()):
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
        update=CAP_Update_CollectionListSelect
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
        update=CAP_Update_ObjectListSelect
        )

    ## FIXME: idk what this is
    action_list: CollectionProperty(type=ActionListItem)
    action_list_index: IntProperty()
    enable_sel_active: BoolProperty(default=False)
    enable_list_active: BoolProperty(default=False)

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

def GetLocationDefaults(scene, context):

    items = [
        ("0", "None",  "", 0),
        ]

    preferences = context.preferences
    addon_prefs = preferences.addons[__package__].preferences
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
    addon_prefs = preferences.addons[__package__].preferences
    exp = bpy.data.objects[addon_prefs.default_datablock].CAPExp

    u = 1

    for i,x in enumerate(exp.file_presets):
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
        update = CAP_Update_ObjectExport
        )

    use_scene_origin: BoolProperty(
        name="Use Scene Origin",
        description="If turned on, the scene's centre will be used as an origin point for the exported object, rather than the object's own origin point.  \n\nIf you have a complex object with many constraints and modifiers and it's not exporting properly without this feature, use this feature <3",
        default=False,
        update=CAP_Update_SceneOrigin
        )

    location_default: EnumProperty(
        name="Select Export Location",
        description="Defines the file path that the object will be exported to.",
        items=GetLocationDefaults,
        update=CAP_Update_LocationDefault
        )

    export_default: EnumProperty(
        name="Select Export Preset",
        description="Defines the export settings used on the object.",
        items=GetExportDefaults,
        update=CAP_Update_ExportDefault
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
        update=CAP_Update_CollectionExport
        )

    root_object: StringProperty(
        name="Origin Object",
        description="Defines the origin point of the exported collection object.  If not defined, the origin will be the scene's origin point.  \n\nIf you have a complex object with many constraints and modifiers and it's not exporting properly with a defined root object, leave it blank <3",
        default="",
        update=CAP_Update_CollectionRootObject
        )

    location_default: EnumProperty(
        name="Select Export Location",
        description="Defines the Location that the collection will be exported to.",
        items=GetLocationDefaults,
        update=CAP_Update_CollectionLocationDefault
        )

    export_default: EnumProperty(
        name="Select Export Default",
        description="Defines the export settings used on the collection.",
        items=GetExportDefaults,
        update=CAP_Update_CollectionExportDefault
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

