from .update import Update_EnableExport, Update_ApplyModifiers, Update_Triangulate, Update_UseCollision, Update_GenerateConvex, Update_SeparateCollision, Update_ExportCollision, Update_CollisionObject, Update_LocationDefault, Update_ExportAnim, Update_ExportAnimFile, Update_ExportAnimActions, Update_GroupItemName

import bpy
from bpy.props import IntProperty, BoolProperty, FloatProperty, EnumProperty, PointerProperty, StringProperty, CollectionProperty
from bpy.types import PropertyGroup
from bpy.app.handlers import persistent

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


class ExportPass(PropertyGroup):

    name = StringProperty(
        name="Pass Name",
        description="The name of the selected pass."
    )

    file_suffix = StringProperty(
        name="File Suffix",
        description="The suffix added on the exported file created from this pass."
    )

    sub_directory = StringProperty(
        name="Sub-Directory",
        description="Export the pass to a new folder inside the chosen location default."
    )

    # Sub-directory?

    export_lp = BoolProperty(
        name="Export Low_Poly",
        description="Selects all low-poly objects available for export.",
        default=False
    )

    export_hp = BoolProperty(
        name="Export High_Poly",
        description="Selects all high-poly objects available for export.",
        default=False
    )

    export_cg = BoolProperty(
        name="Export Cage",
        description="Selects all cage objects available for export.",
        default=False
    )

    export_cx = BoolProperty(
        name="Export Collision",
        description="Selects all collision objects available for export.",
        default=False
    )

    export_ar = BoolProperty(
        name="Export Armature",
        description="Selects all armature objects available for export.",
        default=False
    )

    export_am = BoolProperty(
        name="Export Animation",
        description="Selects all animation objects available for export.",
        default=False
    )

    export_individual = BoolProperty(
        name="Export Individual",
        description="Exports every object in the pass as an individual object.",
        default=False
    )

    apply_modifiers = BoolProperty(
        name="Apply Modifiers",
        description="Applies all modifiers on every object in the pass",
        default=False
    )

    triangulate = BoolProperty(
        name="Triangulate Export",
        description="Triangulate objects in the pass on export using optimal triangulation settings.",
        default=False
    )


class ExportDefault(PropertyGroup):
    name = StringProperty(
        name = "Default Name",
        description="The name of the export default, whoda thunk :OO",
        default=""
    )

    passes = CollectionProperty(type=ExportPass)
    passes_index = IntProperty(default=0)

class GX_Export_Storage(PropertyGroup):
    location_defaults = CollectionProperty(type=LocationDefault)
    location_defaults_index = IntProperty(default=0)

    export_defaults = CollectionProperty(type=ExportDefault)
    export_defaults_index = IntProperty(default=0)


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

    user_preferences = context.user_preferences
    addon_prefs = user_preferences.addons["GEX"].preferences
    defaults = bpy.data.objects[addon_prefs.default_datablock].GXDefaults.location_defaults

    u = 1

    for i,x in enumerate(defaults):

        items.append((str(i+1), x.name, x.name, i+1))

    return items

def GetExportDefaults(scene, context):

    items = [
        ("0", "None",  "", 0),
    ]

    user_preferences = context.user_preferences
    addon_prefs = user_preferences.addons["GEX"].preferences
    defaults = bpy.data.objects[addon_prefs.default_datablock].GXDefaults.export_defaults

    u = 1

    for i,x in enumerate(defaults):

        items.append((str(i+1), x.name, x.name, i+1))

    return items


class GX_Object_Preferences(PropertyGroup):

    enable_export = BoolProperty(
        name = "Enable Export",
        description = "Marks the asset as available for batch exporting using GEX.",
        default = False,
        update = Update_EnableExport)

    auto_assign = BoolProperty(
        name = "Auto Assign Objects",
        description = "Uses naming conventions of objects within a group to automatically assign collision meshes and filter objects for export.",
        default = False)

    location_default = EnumProperty(
        name="Select Location Default",
        description="The filepath default the selected objects will be exported to.",
        items=GetLocationDefaults,
        update=Update_LocationDefault)

    export_default = EnumProperty(
        name = "Select Export Default",
        description = "Defines the export setting sets used on this object.",
        items=GetExportDefaults,
    )

class GX_Group_Preferences(PropertyGroup):

    export_group = BoolProperty(
        name = "Export Group",
        description = "Enables all objects within the group to be exported as a single FBX file.",
        default = False)

    # Should Auto-Assign be a default option?

    auto_assign = BoolProperty(
        name = "Auto Assign Objects",
        description = "Uses naming conventions of objects within a group to automatically assign collision meshes and filter objects for export.",
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

    export_default = EnumProperty(
        name = "Select Export Default",
        description = "Defines the export setting sets used on this object.",
        items=GetExportDefaults,
    )

class GX_UI_Preferences(PropertyGroup):

    component_dropdown = BoolProperty(
        name = "",
        description = "",
        default = False)

    options_dropdown = BoolProperty(
        name = "",
        description = "",
        default = False)

class GX_Object_StateMachine(PropertyGroup):

    has_triangulate = BoolProperty(
        name = "Has Triangulation Modifier",
        description = "Internal variable used to monitor whether or not the object has a Triangulation modifier, when triangulating the mesh ",
        default = False)



# ////////////////////// - CLASS REGISTRATION - ////////////////////////
classes = (LocationDefault, ExportPass, ExportDefault, GroupItem, GX_Export_Storage, GX_Scene_Preferences, GX_Object_Preferences, GX_Group_Preferences, GX_UI_Preferences, GX_Object_StateMachine)

for cls in classes:
    bpy.utils.register_class(cls)

bpy.types.Scene.GXScn = PointerProperty(type=GX_Scene_Preferences)
bpy.types.Object.GXObj = PointerProperty(type=GX_Object_Preferences)
bpy.types.Group.GXGrp = PointerProperty(type=GX_Group_Preferences)
bpy.types.Scene.GXUI = PointerProperty(type=GX_UI_Preferences)
bpy.types.Object.GXStm = PointerProperty(type=GX_Object_StateMachine)
bpy.types.Object.GXDefaults = PointerProperty(type=GX_Export_Storage)


@persistent
def CreateDefaultData(scene):

    user_preferences = bpy.context.user_preferences

    if user_preferences.type == 'NoneType':
        print("ADDON COULD NOT START, CONTACT DEVELOPER FOR ASSISTANCE")
        return

    addon_prefs = user_preferences.addons["GEX"].preferences

    if addon_prefs == None:
        print("ADDON COULD NOT START, CONTACT DEVELOPER FOR ASSISTANCE")
        return

    # Figure out if an object already exists, if yes do nothing
    for object in bpy.data.objects:
        print(object)
        if object.name == addon_prefs.default_datablock:
            return

    # Otherwise create the object using the addon preference data
    bpy.ops.object.select_all(action='DESELECT')
    bpy.ops.object.empty_add(type='PLAIN_AXES')

    defaultDatablock = bpy.context.scene.objects.active
    defaultDatablock.name = addon_prefs.default_datablock
    defaultDatablock.hide = True
    defaultDatablock.hide_render = True
    defaultDatablock.hide_select = True

bpy.app.handlers.load_post.append(CreateDefaultData)
