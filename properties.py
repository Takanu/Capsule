#from .update import Update_VisibilityToggle, Update_ComponentToggle, Update_CompomentListType, Update_VisibilityListType, Update_FreezeList, Update_FreezeDelete, Update_FreezeView, Update_FreezeName, Update_Visibility, Update_ObjectOrigin, Update_ObjectVGOrigin, Update_AssetType, Update_ObjectType, Update_AssetName, Update_BaseName, Update_ComponentName, Update_HP_Visibility, Update_LP_Visibility, Update_CG_Visibility, Update_CG_Visibility, Update_CX_Visibility, Update_BaseVisibility, Update_ComponentVisibility, Update_FreezeVisibility, Update_DummyObject, Update_DummyPosition, Update_DummyLocation, Update_DummyOffset, Update_DummySize, Update_GroupOrigin, Update_XRay, Update_OriginSize

# Ensure you import update statements here

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
        
    path_defaults = CollectionProperty(type=LocationDefault)
    
    path_list_index = IntProperty()
    
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
        default = False)
    
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
        default = False)
    
    use_collision = BoolProperty(
        name = "Use Collision",
        description = "Enables separate exporting of a collision mesh with the selected mesh.",
        default = False)
        
    generate_convex = BoolProperty(
        name = "Convert to Convex Hull",
        description = "Alters the export collision to ensure it's a convex hull, as well as decimates the mesh to optimize collision geometry.  Disabled for separate collision objects.",
        default = False)
    
    separate_collision = BoolProperty(
        name = "Use Separate Collision Object",
        description = "Enables the export of a separate object to use as collision for the currently selected object.",
        default = False)
        
    collision_object = StringProperty(
        name="",
        description="The name of the collision object to be used.",
        default="")
        
    export_collision = BoolProperty(
        name = "Export Collision As File",
        description = "Allows the selected collision mesh to be exported as a separate file alongside the selected mesh.",
        default = False)
        
    location_default = EnumProperty(
        name="Select Location Default",
        description="The filepath default the selected objects will be exported to.",
        items=GetLocationDefaults)


# ////////////////////// - CLASS REGISTRATION - ////////////////////////
classes = (LocationDefault, GX_Scene_Preferences, GX_Object_Preferences)

for cls in classes:
    bpy.utils.register_class(cls)

bpy.types.Scene.GXScn = PointerProperty(type=GX_Scene_Preferences)
bpy.types.Object.GXObj = PointerProperty(type=GX_Object_Preferences)
