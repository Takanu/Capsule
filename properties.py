from .update import Update_EnableExport, Update_AutoAssign, Update_LocationDefault, Update_ExportDefault, Update_ObjectItemName, Update_ObjectItemExport, Update_GroupItemName, Update_ActionItemName

import bpy
from bpy.props import IntProperty, BoolProperty, FloatProperty, EnumProperty, PointerProperty, StringProperty, CollectionProperty
from bpy.types import PropertyGroup

class ObjectItem(PropertyGroup):
    name = StringProperty(
        name="",
        description="The name of the group.",
        update=Update_ObjectItemName
    )

    prev_name = StringProperty(
        name="",
        description="Internal only, used for tracking name updates."
    )

    enable_export = BoolProperty(
        name="",
        description="",
        default=False,
        update=Update_ObjectItemExport
    )

class GroupItem(PropertyGroup):
    name = StringProperty(
        name="",
        description="The name of the group.",
        update=Update_GroupItemName
    )

    prev_name = StringProperty(
        name="",
        description="Internal only, used for tracking name updates."
    )

class ActionItem(PropertyGroup):
    name = StringProperty(
        name="",
        description="The name of the action.",
        update=Update_ActionItemName
    )

    prev_name = StringProperty(
        name="",
        description="Internal only, used for tracking name updates."
    )

    anim_type = EnumProperty(
        name = "Animation Data Type",
        description = "Switches the selection editing mode between individual, selected objects, and groups that can be browsed and edited through a list.",
        items=(
        ('1', 'Action Object', ''),
        ('2', 'NLA Object', ''),
        ('3', 'Action Armature', ''),
        ('4', 'NLA Armature', ''),
        ),)

class LocationDefault(PropertyGroup):
    name = StringProperty(
        name="",
        description="The name of the file path default.")

    path = StringProperty(name="",
        description="The file path to export the object to.",
        default="",
        subtype="FILE_PATH")


class GX_Scene_Preferences(PropertyGroup):

    engine_select = EnumProperty(
        name="Set Game Engine",
        items=(
        ('1', 'Unreal Engine 4', 'Configures export and export options for Unreal Engine 4'),
        ('2', 'Unity 5', 'Configures export and export options for Unity'),
        ),)

    scale_100x = BoolProperty(
        name="Scale 100x",
        description="Scales every exported object by 100 times its original size in order to correct asset scales for Unreal Engine 4.7 or lower",
        default=False)

    correct_rotation = BoolProperty(
        name="Correct Rotation",
        description="Rotates all assets 180º on the Z axis before exporting, to appear in the same orientation in Unity as it does currently.",
        default=False)

    group_list = CollectionProperty(type=GroupItem)
    group_list_index = IntProperty()

    object_list = CollectionProperty(type=ObjectItem)
    object_list_index = IntProperty()

    location_defaults = CollectionProperty(type=LocationDefault)
    location_defaults_index = IntProperty(default=0)

    object_switch = EnumProperty(
        name = "Object Type Switch",
        description = "Switches the selection editing mode between individual, selected objects, and groups that can be browsed and edited through a list.",
        items=(
        ('1', 'Individual', 'Enables property editing for all selected static objects'),
        ('2', 'Group', 'Enables property editing for all selected skeletal objects')
        ),)

def GetLocationDefaults(scene, context):

    items = [
        ("0", "None",  "", 0),
    ]

    scn = context.scene.GXScn

    u = 1

    for i,x in enumerate(scn.location_defaults):

        items.append((str(i+1), x.name, x.name, i+1))

    return items

def GetExportDefaults(scene, context):

    items = [
        ("0", "None",  "", 0),
    ]

    user_preferences = context.user_preferences
    addon_prefs = user_preferences.addons["GEX"].preferences

    u = 1

    for i,x in enumerate(addon_prefs.export_defaults):

        items.append((str(i+1), x.name, x.name, i+1))

    return items


class GX_Object_Preferences(PropertyGroup):
    enable_export = BoolProperty(
        name = "Enable Export",
        description = "Marks the asset as available for batch exporting using GEX.",
        default = False,
        update = Update_EnableExport)

    location_default = EnumProperty(
        name="Select Location Default",
        description="The filepath default the selected objects will be exported to.",
        items=GetLocationDefaults,
        update=Update_LocationDefault)

    export_default = EnumProperty(
        name = "Select Export Default",
        description = "Defines the export setting sets used on this object.",
        items=GetExportDefaults,
        update=Update_ExportDefault)


class GX_Group_Preferences(PropertyGroup):
    export_group = BoolProperty(
        name = "Export Group",
        description = "Enables all objects within the group to be exported as a single FBX file.",
        default = False)

    root_object = StringProperty(
        name = "Root Object",
        description = "Defines the object that the origin will be fixed to.",
        default = "")

    location_default = EnumProperty(
        name="Select Location Default",
        description="The filepath default the selected group will be exported to.",
        items=GetLocationDefaults)

    export_default = EnumProperty(
        name = "Select Export Default",
        description = "Defines the export setting sets used on this object.",
        items=GetExportDefaults)

class GX_UI_Preferences(PropertyGroup):
    component_dropdown = BoolProperty(
        name = "",
        description = "",
        default = False)

    options_dropdown = BoolProperty(
        name = "",
        description = "",
        default = False)

    action_list = CollectionProperty(type=ActionItem)

    action_list_index = IntProperty()

class GX_Object_StateMachine(PropertyGroup):

    has_triangulate = BoolProperty(
        name = "Has Triangulation Modifier",
        description = "Internal variable used to monitor whether or not the object has a Triangulation modifier, when triangulating the mesh ",
        default = False)

class GX_Action_Preferences(PropertyGroup):
    export = BoolProperty(
        name = "Export",
        description = "Determines whether the action can be exported or not.",
        default = True)


# ////////////////////// - CLASS REGISTRATION - ////////////////////////
classes = (ObjectItem, GroupItem, ActionItem, LocationDefault, GX_Scene_Preferences, GX_Object_Preferences, GX_Group_Preferences, GX_UI_Preferences, GX_Object_StateMachine, GX_Action_Preferences)

for cls in classes:
    bpy.utils.register_class(cls)

bpy.types.Scene.GXScn = PointerProperty(type=GX_Scene_Preferences)
bpy.types.Object.GXObj = PointerProperty(type=GX_Object_Preferences)
bpy.types.Group.GXGrp = PointerProperty(type=GX_Group_Preferences)
bpy.types.Action.GXAcn = PointerProperty(type=GX_Action_Preferences)
bpy.types.Scene.GXUI = PointerProperty(type=GX_UI_Preferences)
bpy.types.Object.GXStm = PointerProperty(type=GX_Object_StateMachine)
