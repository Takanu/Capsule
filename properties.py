from .update import Update_EnableExport, Update_ApplyModifiers, Update_Triangulate, Update_UseCollision, Update_GenerateConvex, Update_SeparateCollision, Update_ExportCollision, Update_CollisionObject, Update_LocationDefault, Update_ExportAnim, Update_ExportAnimFile, Update_ExportAnimActions


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

class GX_Scene_Preferences(PropertyGroup):

    engine_select = EnumProperty(
        name="Set Game Engine",
        items=(
        ('1', 'Unreal Engine 4', 'Configures export and export options for Unreal Engine 4'),
        ('2', 'Unity 5', 'Configures export and export options for Unity'),
        ('3', 'OpenGEX', 'Configures export and export options for the OpenGEX format.')
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
        description = "Marks the asset as available for batch exporting export using GEX.",
        default = False,
        update = Update_EnableExport)

    asset_type = EnumProperty(
        name="Asset Type",
        items=(
        ('1', 'Static', 'Used for objects with no animation properties.'),
        ('2', 'Skeletal', 'Used for objects with animation properties through the use of an Armature.'),
        ('3', 'Animation', 'Used to export the animations of a selected armature exclusively.'),
        ),)

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


# ////////////////////// - CLASS REGISTRATION - ////////////////////////
classes = (LocationDefault, GX_Scene_Preferences, GX_Object_Preferences)

for cls in classes:
    bpy.utils.register_class(cls)

bpy.types.Scene.GXScn = PointerProperty(type=GX_Scene_Preferences)
bpy.types.Object.GXObj = PointerProperty(type=GX_Object_Preferences)
