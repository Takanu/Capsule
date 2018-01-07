
import bpy
from bpy.props import IntProperty, BoolProperty, FloatProperty, EnumProperty, PointerProperty, StringProperty, CollectionProperty
from bpy.types import PropertyGroup

from .update import CAP_Update_ObjectExport, CAP_Update_SceneOrigin, CAP_Update_LocationDefault, CAP_Update_ExportDefault, CAP_Update_Normals, CAP_Update_ObjectListName, CAP_Update_ObjectListExport, CAP_Update_ActionItemName, CAP_Update_FocusObject,  CAP_Update_SelectObject, CAP_Update_ObjectListSelect, CAP_Update_ObjectRemoveFromList

from .update_groups import CAP_Update_GroupListName, CAP_Update_GroupListExport, CAP_Update_FocusGroup, CAP_Update_SelectGroup, CAP_Update_GroupExport, CAP_Update_GroupRootObject, CAP_Update_GroupExportDefault, CAP_Update_GroupLocationDefault, CAP_Update_GroupNormals, CAP_Update_GroupListSelect, CAP_Update_GroupRemoveFromList

class ObjectListItem(PropertyGroup):
    """
    Defines an object as a list property, for use when displaying objects in the user interface.
    """
    name = StringProperty(
        name="",
        description="The name of the group.",
        update=CAP_Update_ObjectListName
        )

    prev_name = StringProperty(
        name="",
        description="Internal only, used for tracking name updates."
        )

    enable_export = BoolProperty(
        name="",
        description="Enables or disables the ability to export this object.",
        default=False,
        update=CAP_Update_ObjectListExport
        )

    sel = BoolProperty(
        name="Select",
        description="Selects the object in the scene",
        default=True,
        update=CAP_Update_SelectObject
        )

    focus = BoolProperty(
        name="Focus",
        description="Focuses the camera to the object",
        default=True,
        update=CAP_Update_FocusObject
        )

    remove = BoolProperty(
        name="",
        description="Removes the object from the list, and un-marks it for export.",
        default=True,
        update=CAP_Update_ObjectRemoveFromList
        )

class GroupListItem(PropertyGroup):
    """
    Defines a group as a list property, for use when displaying groups in the user interface.
    """
    name = StringProperty(
        name="",
        description="The name of the group.",
        update=CAP_Update_GroupListName
        )

    prev_name = StringProperty(
        name="",
        description="Internal only, used for tracking name updates."
        )

    enable_export = BoolProperty(
        name="",
        description="Enables or disables the ability to export this group.",
        default=False,
        update=CAP_Update_GroupListExport
        )

    sel = BoolProperty(
        name="Select",
        description="Selects the group in the scene",
        default=True,
        update=CAP_Update_SelectGroup
        )

    focus = BoolProperty(
        name="Focus Export",
        description="Focuses the camera to the entire group.",
        default=True,
        update=CAP_Update_FocusGroup
        )

    remove = BoolProperty(
        name="",
        description="Removes the group from the list, and un-marks it for export.",
        default=True,
        update=CAP_Update_GroupRemoveFromList
        )

class ActionListItem(PropertyGroup):
    """
    Defines an animation action as a list property, for use when displaying actions in the user interface.
    """
    name = StringProperty(
        name="",
        description="The name of the action.",
        update=CAP_Update_ActionItemName
        )

    prev_name = StringProperty(
        name="",
        description="Internal only, used for tracking name updates."
        )

    anim_type = EnumProperty(
        name="Animation Data Type",
        description="Switches the selection editing mode between individual, selected objects, and groups that can be browsed and edited through a list.",
        items=(
        ('1', 'Action Object', ''),
        ('2', 'NLA Object', ''),
        ('3', 'Action Armature', ''),
        ('4', 'NLA Armature', ''),),
        )

def GetSelectedGroups(scene, context):

    items = [
        ("0", "None",  "", 0),
        ]

    scn = context.scene.CAPScn
    scn.group_selected_list.clear()
    groups_found = []

    for item in context.selected_objects:
        for group in item.users_group:
            groupAdded = False

            for found_group in groups_found:
                if found_group.name == group.name:
                    groupAdded = True

            if groupAdded == False:
                groups_found.append(group)

    u = 1

    for i,x in enumerate(groups_found):
        items.append((str(i+1), x.name, x.name, i+1))
        newGroup = scn.group_selected_list.add()
        newGroup.name = x.name

    return items

class CAP_Scene_Preferences(PropertyGroup):
    """
    A random assortment of scene-specific properties with some "weird" toggle stuff.
    """

    # A collection that stores the list of groups that Capsule is currently displaying in the UI list.
    group_list = CollectionProperty(type=GroupListItem)

    # ???
    group_list_index = IntProperty(
        name="",
        description="",
        update=CAP_Update_GroupListSelect
        )

    ## ???
    group_selected_list = CollectionProperty(type=GroupListItem)

    ## ???
    group_selected_list_enum = EnumProperty(items=GetSelectedGroups)

    ## The index of the currently selected group from the UI list.  Will be -1 if not selected.
    group_selected_list_index = IntProperty()

    # A collection that stores the list of objects that Capsule is currently displaying in the UI list.
    object_list = CollectionProperty(type=ObjectListItem)

    # ???
    object_list_index = IntProperty(name="",
        description="",
        update=CAP_Update_ObjectListSelect
        )

    ## FIXME: idk what this is
    action_list = CollectionProperty(type=ActionListItem)
    action_list_index = IntProperty()
    enable_sel_active = BoolProperty(default=False)
    enable_list_active = BoolProperty(default=False)

    list_switch = EnumProperty(
        name="Object Type Switch",
        description="Switches the list display mode between objects and groups.",
        items=(
        ('1', 'Objects', 'Displays the Export List for objects in the currently visible scene.'),
        ('2', 'Groups', 'Displays the Export List for groups in the currently visible scene')),
        )

    selection_switch = EnumProperty(
        name="Selection Switch",
        description="Switches the selection editing mode between objects and groups.",
        items=(
        ('1', 'Objects', 'Displays selected objects, and any associated export settings.'),
        ('2', 'Groups', 'Displays selected groups, and any associated export settings.')),
        )

def GetLocationDefaults(scene, context):

    items = [
        ("0", "None",  "", 0),
        ]

    user_preferences = context.user_preferences
    addon_prefs = user_preferences.addons[__package__].preferences
    exp = bpy.data.objects[addon_prefs.default_datablock].CAPExp

    u = 1

    for i,x in enumerate(exp.location_presets):
        items.append((str(i+1), x.name, x.name, i+1))

    return items

def GetExportDefaults(scene, context):

    items = [
        ("0", "None",  "", 0),
        ]

    user_preferences = context.user_preferences
    addon_prefs = user_preferences.addons[__package__].preferences
    exp = bpy.data.objects[addon_prefs.default_datablock].CAPExp

    u = 1

    for i,x in enumerate(exp.file_presets):
        items.append((str(i+1), x.name, x.name, i+1))

    return items

class CAP_Object_Preferences(PropertyGroup):
    """
    A special property block that all objects receive when Capsule is registered, allowing it to store
    required information to manage it as a potential export target.
    """

    enable_export = BoolProperty(
        name = "Enable Export",
        description = "Enables or disables the ability to export this object.",
        default = False,
        update = CAP_Update_ObjectExport
        )

    use_scene_origin = BoolProperty(
        name="Use Scene Origin",
        description="If turned on, the scene's centre will be used as an origin point for the exported object, rather than the object's own origin point.  \n\nIf you have a complex object with many constraints and modifiers and it's not exporting properly without this feature, use this feature <3",
        default=False,
        update=CAP_Update_SceneOrigin
        )

    location_default = EnumProperty(
        name="Select Location Preset",
        description="Defines the file path that the object will be exported to.",
        items=GetLocationDefaults,
        update=CAP_Update_LocationDefault
        )

    export_default = EnumProperty(
        name="Select Export Preset",
        description="Defines the export settings used on the object.",
        items=GetExportDefaults,
        update=CAP_Update_ExportDefault
        )

    in_export_list = BoolProperty(
        name="",
        description="(Internal Only) Prevents refreshes of the Export List from removing items not marked for export.",
        default=False
        )

class CAP_Group_Preferences(PropertyGroup):
    """
    A special property block that all groups receive when Capsule is registered, allowing it to store
    required information to manage it as a potential export target.
    """
    enable_export = BoolProperty(
        name="Export Group",
        description="Enables or disables the ability to export this group.",
        default=False,
        update=CAP_Update_GroupExport
        )

    root_object = StringProperty(
        name="Origin Object",
        description="Defines the origin point of the exported group object.  If not defined, the origin will be the scene center point.  \n\nIf you have a complex object with many constraints and modifiers and it's not exporting properly with a defined root object, leave it blank <3",
        default="",
        update=CAP_Update_GroupRootObject
        )

    location_default = EnumProperty(
        name="Select Location Default",
        description="Defines the Location that the group will be exported to.",
        items=GetLocationDefaults,
        update=CAP_Update_GroupLocationDefault
        )

    export_default = EnumProperty(
        name="Select Export Default",
        description="Defines the export settings used on the group.",
        items=GetExportDefaults,
        update=CAP_Update_GroupExportDefault
        )

    in_export_list = BoolProperty(
        name="",
        description="(Internal Only) Prevents refreshes of the Export List from removing items not marked for export.",
        default=False
        )

def GetExportPresets(scene, context):

    items = []
    user_preferences = context.user_preferences
    addon_prefs = user_preferences.addons["Blinkey"].preferences

    u = 1

    for i,x in enumerate(addon_prefs.presets):
        items.append((str(i), x.name, x.name, i))

    return items

class CAP_Object_StateMachine(PropertyGroup):

    has_triangulate = BoolProperty(
        name="Has Triangulation Modifier",
        description="Internal variable used to monitor whether or not the object has a Triangulation modifier, when triangulating the mesh ",
        default=False
        )

class CAP_Action_Preferences(PropertyGroup):
    export = BoolProperty(
        name="Export",
        description="Determines whether the action can be exported or not.",
        default=True
        )


# ////////////////////// - CLASS REGISTRATION - ////////////////////////
classes = (ObjectListItem, GroupListItem, ActionListItem, CAP_Scene_Preferences, CAP_Object_Preferences, CAP_Group_Preferences, CAP_Object_StateMachine, CAP_Action_Preferences)

def register():
    print("Registering Properties")
    for item in classes:
        bpy.utils.register_class(item)

    bpy.types.Scene.CAPScn = PointerProperty(type=CAP_Scene_Preferences)
    bpy.types.Object.CAPObj = PointerProperty(type=CAP_Object_Preferences)
    bpy.types.Group.CAPGrp = PointerProperty(type=CAP_Group_Preferences)
    bpy.types.Action.CAPAcn = PointerProperty(type=CAP_Action_Preferences)
    bpy.types.Scene.CAPUI = PointerProperty(type=CAP_UI_Preferences)
    bpy.types.Object.CAPStm = PointerProperty(type=CAP_Object_StateMachine)

def unregister():
    print("Un-registering Properties")
    del bpy.types.Scene.CAPScn
    del bpy.types.Object.CAPObj
    del bpy.types.Group.CAPGrp
    del bpy.types.Action.CAPAcn
    del bpy.types.Scene.CAPUI
    del bpy.types.Object.CAPStm

    i = len(classes) - 1
    while i != -1:
        bpy.utils.unregister_class(classes[i])
