from .update import Update_EnableExport, Update_AutoAssign, Update_LocationDefault, Update_ExportDefault, Update_Normals, Update_ObjectItemName, Update_ObjectItemExport, Update_GroupItemName, Update_ActionItemName, Focus_Object, Focus_Group, Select_Object, Select_Group, Update_GroupExport, Update_GroupRootObject, Update_GroupExportDefault, Update_GroupLocationDefault, Update_GroupNormals

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

    sel = BoolProperty(
        name = "Select",
        description = "Selects the object in the scene",
        default = True,
        update = Select_Object)

    focus = BoolProperty(
        name = "Focus",
        description = "Focuses the camera to the object",
        default = True,
        update = Focus_Object)

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

    sel = BoolProperty(
        name = "Select",
        description = "Selects the group in the scene",
        default = True,
        update = Select_Group)

    focus = BoolProperty(
        name = "Focus Export",
        description = "Focuses the camera to the entire group.",
        default = True,
        update = Focus_Group)


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

def GetSelectedGroups(scene, context):

    items = [
        ("0", "None",  "", 0),
    ]

    scn = context.scene.GXScn
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


class GX_Scene_Preferences(PropertyGroup):

    engine_select = EnumProperty(
        name="Set Game Engine",
        items=(
        ('1', 'Unreal Engine 4', 'Configures export and export options for Unreal Engine 4'),
        ('2', 'Unity 5', 'Configures export and export options for Unity'),
        ),)

    correct_rotation = BoolProperty(
        name="Correct Rotation",
        description="Rotates all assets 180º on the Z axis before exporting, to appear in the same orientation in Unity as it does currently.",
        default=False)


    group_list = CollectionProperty(type=GroupItem)
    group_list_index = IntProperty()

    group_selected_list = CollectionProperty(type=GroupItem)
    group_selected_list_enum = EnumProperty(items=GetSelectedGroups)
    group_selected_list_index = IntProperty()

    object_list = CollectionProperty(type=ObjectItem)
    object_list_index = IntProperty()

    location_defaults = CollectionProperty(type=LocationDefault)
    location_defaults_index = IntProperty(default=0)

    object_switch = EnumProperty(
        name = "Object Type Switch",
        description = "Switches the selection editing mode between individual, selected objects, and groups that can be browsed and edited through a list.",
        items=(
        ('1', 'Objects', 'Switches to the Object menu, for editing the exports of single objects and any tags associated with them.'),
        ('2', 'Groups', 'Switches to the Group menu, for editing the exports of groups.')
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
    addon_prefs = user_preferences.addons[__package__].preferences

    u = 1

    for i,x in enumerate(addon_prefs.export_defaults):

        items.append((str(i+1), x.name, x.name, i+1))

    return items


class GX_Object_Preferences(PropertyGroup):
    enable_export = BoolProperty(
        name = "Enable Export",
        description = "Enables the object and any matching, tagged objects to be exported as a single FBX file through GEX.",
        default = False,
        update = Update_EnableExport)

    use_scene_origin = BoolProperty(
        name = "Use Scene Origin",
        description = "Uses the scene's centre as an origin point for the object export, rather than the object's own origin point.",
        default = False
    )

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

    normals = EnumProperty(
        name = "Normal Export Type",
        description = "Defines how the mesh normals are exported.",
        items=(
        ('1', 'Edge', 'Writes edge smoothing data for the mesh in the FBX file.'),
        ('2', 'Face', 'Writes face smoothing data for the mesh in the FBX file.'),
        ('3', 'Normals Only', 'Exports the current custom normals of the model.')
        ),
        update=Update_Normals)


class GX_Group_Preferences(PropertyGroup):
    export_group = BoolProperty(
        name = "Export Group",
        description = "Enables all objects within the group to be exported as a single FBX file through GEX.",
        default = False,
        update=Update_GroupExport)

    root_object = StringProperty(
        name = "Root Object",
        description = "Defines the exported origin point of the group object.  If not defined, the origin will be the world center.",
        default = "",
        update=Update_GroupRootObject)

    location_default = EnumProperty(
        name="Select Location Default",
        description="The filepath default the selected group will be exported to.",
        items=GetLocationDefaults,
        update=Update_GroupLocationDefault)

    export_default = EnumProperty(
        name = "Select Export Default",
        description = "Defines the export setting sets used on this object.",
        items=GetExportDefaults,
        update=Update_GroupExportDefault)

    normals = EnumProperty(
        name = "Normal Export Type",
        description = "Defines how the mesh normals are exported.",
        items=(
        ('1', 'Edge', 'Writes edge smoothing data for the mesh in the FBX file.'),
        ('2', 'Face', 'Writes face smoothing data for the mesh in the FBX file.'),
        ('3', 'Normals Only', 'Exports the current custom normals of the model.')
        ),
        update=Update_GroupNormals)

def GetExportPresets(scene, context):

    items = []
    user_preferences = context.user_preferences
    addon_prefs = user_preferences.addons["Blinkey"].preferences

    u = 1

    for i,x in enumerate(addon_prefs.presets):

        items.append((str(i), x.name, x.name, i))

    return items

class GX_UI_Preferences(PropertyGroup):
    export_presets = EnumProperty(
        name = "Export Presets",
        description = "List of available visibility presets.",
        items = GetExportPresets
    )

    presets_dropdown = BoolProperty(default = False)
    tags_dropdown = BoolProperty(default = False)
    passes_dropdown = BoolProperty(default = False)
    options_dropdown = BoolProperty(default = False)

    action_list = CollectionProperty(type=ActionItem)
    action_list_index = IntProperty()

    custom_presets = EnumProperty(
    name = "Custom Presets",
    description = "Adds a special preset that changes how objects are processed for export, making exports from Blender to other programs smoother.",
    items=(
    ('1', 'Unreal Engine 4 Standard', 'Sets up a custom preset for UE4, with support for multiple collision objects per low_poly and seamless collision importing.'),
    ('2', 'Unity 5', 'Sets up a custom preset for Unity, which in conjunction with the included import script, supports collision components with the base mesh in one file.'),
    ('3', '3DS Max', 'Hahahaha, just kidding.')
    ),)

    enable_export_loop = BoolProperty(default = False)

    export_preset_options = EnumProperty(
        name = "Export Options",
        description = "",
        items=(
        ('Export', 'Export', 'A tab containing additional export paramaters exclusive to Capsule.'),
        ('Transform', 'Transform', 'A tab containing options to how objects are scaled and orientated in the export.'),
        ('Geometry', 'Geometry', 'A tab containing options for how object geometry is interpreted in the export.'),
        ('Armature', 'Armature', 'A tab containing options for how armature objects are interpreted in the export.'),
        ('Animation', 'Animation', 'A tab containing options for how animations are interpreted and used in the export.')
        ),)

    object_multi_edit = BoolProperty(
        name = "Group Multi-Edit Mode",
        description = "Allows you to edit export settings for all objects that the currently selected.  Turning this option off will let you edit the currently selected object on the list.",
        default=True)

    group_multi_edit = BoolProperty(
        name = "Group Multi-Edit Mode",
        description = "Allows you to edit export settings for all groups that the currently selected objects belong to.  WARNING - One object can belong to multiple groups, please be careful when using this mode.",
        default=False)

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
