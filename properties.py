from .update import Update_EnableExport, Update_ApplyModifiers, Update_Triangulate, Update_UseCollision, Update_GenerateConvex, Update_SeparateCollision, Update_ExportCollision, Update_CollisionObject, Update_LocationDefault, Update_ExportAnim, Update_ExportAnimFile, Update_ExportAnimActions, Update_GroupItemName


import bpy
from bpy.props import IntProperty, BoolProperty, FloatProperty, EnumProperty, PointerProperty, StringProperty, CollectionProperty

from bpy.types import PropertyGroup

class LocationDefault(PropertyGroup):
    name = StringProperty(
        name="",
        description="The name of the file path default.")

    path = StringProperty(name="",
        description="The file path to export the object to.",
        default="",
        subtype="FILE_PATH")


class GroupItem(PropertyGroup):
    name = StringProperty(
        name="",
        description="The name of the file path default.",
        update=Update_GroupItemName)

    prev_name = StringProperty(
        name="",
        description="Internal only, used for tracking group name updates.")


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

    path_defaults = CollectionProperty(type=LocationDefault)

    path_list_index = IntProperty()

    group_list = CollectionProperty(type=GroupItem)

    group_list_index = IntProperty()

    object_switch = EnumProperty(
        name = "Object Type Switch",
        description = "Switches the selection editing mode between individual, selected objects, and groups that can be browsed and edited through a list.",
        items=(
        ('1', 'Individual', 'Enables property editing for all selected static objects'),
        ('2', 'Group', 'Enables property editing for all selected skeletal objects')
        ),)

    type_switch = EnumProperty(
        name = "Selection Type Switch",
        description = "Switches the selection editing mode between Static and Skeletal Mesh objects",
        items=(
        ('1', 'Static', 'Enables property editing for all selected static objects'),
        ('2', 'Skeletal', 'Enables property editing for all selected skeletal objects')
        ),)

def GetLocationDefaults(scene, context):

    items = [
        ("0", "None",  "", 0),
    ]

    scn = context.scene.GXScn
    default = scn.path_defaults

    u = 1

    for i,x in enumerate(default):

        items.append((str(i+1), x.name, x.name, i+1))

    return items


class GX_Object_Preferences(PropertyGroup):

    enable_export = BoolProperty(
        name = "Enable Export",
        description = "Marks the asset as available for batch exporting using GEX.",
        default = False,
        update = Update_EnableExport)

    apply_modifiers = BoolProperty(
        name = "Apply Modifiers",
        description = "Decide whether the selected object is exported with modifiers applied or not",
        default = False,
        update = Update_ApplyModifiers)

    triangulate = BoolProperty(
        name = "Triangulate Export",
        description = "Enable automatic asset triangulation, using a Fixed Alternate Quad conversion method with a Clip N-Gon conversion method.",
        default = False,
        update = Update_Triangulate)

    use_collision = BoolProperty(
        name = "Export Collision",
        description = "Enables separate exporting of a collision mesh with the selected mesh.",
        default = False,
        update=Update_UseCollision)

    generate_convex = BoolProperty(
        name = "Convert to Convex Hull",
        description = "Alters the export collision to ensure it's a convex hull, as well as decimates the mesh to optimize collision geometry.  Disabled for separate collision objects.",
        default = False,
        update = Update_GenerateConvex)

    separate_collision = BoolProperty(
        name = "Use Separate Collision Object",
        description = "Enables the export of a separate object to use as collision for the currently selected object.",
        default = False,
        update = Update_SeparateCollision)

    collision_object = StringProperty(
        name="",
        description="The name of the collision object to be used.",
        default="")

    export_collision = BoolProperty(
        name = "Export Collision As File",
        description = "Allows the selected collision mesh to be exported as a separate file alongside the selected mesh.",
        default = False,
        update = Update_ExportCollision)

    location_default = EnumProperty(
        name="Select Location Default",
        description="The filepath default the selected objects will be exported to.",
        items=GetLocationDefaults,
        update=Update_LocationDefault)

    export_anim = BoolProperty(
        name = "Export Animation",
        description = "Enables the animations of skeletal meshes to be exported",
        default = False,
        update = Update_ExportAnim)

    export_anim_file = BoolProperty(
        name = "Export Animation as File",
        description = "Exports the animation as a separate file instead of being embedded in the same file as the skeletal mesh.",
        default = False,
        update = Update_ExportAnimFile)

    export_anim_actions = BoolProperty(
        name = "Export Selected Actions",
        description = "Enables the display of an action list, that lets you select what actions to export from the skeletal meshes selected.",
        default = False,
        update = Update_ExportAnimActions)

class GX_Group_Preferences(PropertyGroup):

    export_group = BoolProperty(
        name = "Export Group",
        description = "Enables all objects within the group to be exported as a single FBX file.",
        default = False)

    auto_assign = BoolProperty(
        name = "Auto Assign Objects",
        description = "Uses naming conventions of objects within a group to automatically assign collision meshes and filter objects for export.",
        default = False)

    apply_modifiers = BoolProperty(
        name = "Apply Modifiers",
        description = "Apply all modifiers for all exportable objects on export.",
        default = False)

    triangulate = BoolProperty(
        name = "Triangulate Export",
        description = "Enable automatic asset triangulation, using a Fixed Alternate Quad conversion method with a Clip N-Gon conversion method for all exportable objects in the group.",
        default = False)

    root_object = StringProperty(
        name = "Root Object",
        description = "Defines the object that the origin will be fixed to.",
        default = ""
    )
    location_default = EnumProperty(
        name="Select Location Default",
        description="The filepath default the selected group will be exported to.",
        items=GetLocationDefaults)

    export_lp = BoolProperty(
        name = "Low-Poly",
        description = "Export all low-poly objects as a separate FBX file.",
        default = False)

    export_hp = BoolProperty(
        name = "High-Poly",
        description = "Export all high-poly objects as a separate FBX file.",
        default = False)

    export_cg = BoolProperty(
        name = "Cage",
        description = "Export all cage objects as a separate FBX file.",
        default = False)

    export_cx = BoolProperty(
        name = "Collision",
        description = "Export all collision objects as a separate FBX file.",
        default = False)

class GX_UI_Preferences(PropertyGroup):

    group_separate_dropdown = BoolProperty(
        name = "",
        description = "",
        default = False)

    group_options_dropdown = BoolProperty(
        name = "",
        description = "",
        default = False)

class GX_Object_StateMachine(PropertyGroup):

    has_triangulate = BoolProperty(
        name = "Has Triangulation Modifier",
        description = "Internal variable used to monitor whether or not the object has a Triangulation modifier, when triangulating the mesh ",
        default = False)

# ////////////////////// - CLASS REGISTRATION - ////////////////////////
classes = (LocationDefault, GroupItem, GX_Scene_Preferences, GX_Object_Preferences, GX_Group_Preferences, GX_UI_Preferences, GX_Object_StateMachine)

for cls in classes:
    bpy.utils.register_class(cls)

bpy.types.Scene.GXScn = PointerProperty(type=GX_Scene_Preferences)
bpy.types.Object.GXObj = PointerProperty(type=GX_Object_Preferences)
bpy.types.Group.GXGrp = PointerProperty(type=GX_Group_Preferences)
bpy.types.Scene.GXUI = PointerProperty(type=GX_UI_Preferences)
bpy.types.Object.GXStm = PointerProperty(type=GX_Object_StateMachine)
