
import bpy
import copy

from bpy.types import Operator
from bpy.props import IntProperty, BoolProperty, FloatProperty, EnumProperty, PointerProperty, StringProperty, CollectionProperty

def DeletePresets():
    """
    Removes all Export Presets that that can be deleted by the user from the saved presets list.
    """
    print(">>>>>>>>>> Deleting presets...")
    user_preferences = bpy.context.user_preferences
    addon_prefs = user_preferences.addons[__package__].preferences
    exp = addon_prefs.saved_presets
    presetsToKeep = []

    i = len(exp) - 1
    print("i = ", i)

    while i != -1:
        item = exp[i]
        print("item = ", item)
        if item.x_global_user_deletable is False:
            print("Removing default exp...", exp[i])
            exp.remove(i)
        i -= 1


def CreatePresets():
    """
    Generates a list of saved presets based on pre-made templates.
    """

    # -------------------------------------------------------------------------
    # Basic Export All
    # -------------------------------------------------------------------------
    user_preferences = bpy.context.user_preferences
    addon_prefs = user_preferences.addons[__package__].preferences
    exp = addon_prefs.saved_presets
    sort = addon_prefs.sort_presets
    print(">>>>>>>>>> Adding presets...")

    # Erase the previous sort entries (delayed)
    print("Clearing sort presets")
    x = 0
    lenX = len(sort)
    while x < lenX:
        print("Deleting sort preset...", sort[0])
        sort.remove(0)
        x += 1

    # Copy all the currently-saved presets to a temporary sort preset location.
    i = 0
    lenI = len(exp)
    print("lenI = ", lenI)
    print("Saving Presets...")
    print(exp)
    while i < lenI:
        if exp[0].x_global_user_deletable is True:
            print("Copying user-defined preset...", exp[0])
            newPreset = sort.add()
            CopyPreset(exp[0], newPreset)

        print("Deleting preset...", exp[0])
        exp.remove(0)
        i += 1

    # Create the new presets
    CreatePresetBasicExport(exp)
    CreatePresetUE4Standard(exp)
    CreatePresetUnity5Standard(exp)

    # Add the copied presets back
    i = 0
    lenI = len(sort)
    print(sort)
    while i < lenI:
        print("Adding back preset...", sort[0])
        newPreset = exp.add()
        CopyPreset(sort[0], newPreset)
        sort.remove(0)
        i += 1

def CreatePresetBasicExport(exp):
    """
    Generates a basic saved export preset.
    """
    # -------------------------------------------------------------------------
    # Basic Export All
    # -------------------------------------------------------------------------
    export = exp.add()
    export.name = "Basic Export All"
    export.description = "Creates a basic Export Preset with ideal settings for most purposes."
    export.x_global_user_deletable = False

    export.data_fbx.axis_forward = "-Z"
    export.data_fbx.axis_up = "Y"
    export.data_fbx.global_scale = 1.0
    export.data_fbx.apply_unit_scale = True

    passOne = export.passes.add()
    passOne.name = "Combined Pass"
    passOne.export_animation_prev = False
    passOne.export_animation = False
    passOne.apply_modifiers = True
    passOne.triangulate = True

def CreatePresetUE4Standard(exp):
    """
    Generates a saved preset for exporting UE4-compatible assets.
    """
    # -------------------------------------------------------------------------
    # UE4 Standard Template
    # -------------------------------------------------------------------------
    export = exp.add()
    export.name = "UE4 Standard"
    export.description = "Creates an Export Preset for exporting FBX files for Unreal Engine 4, with optimised settings.  Enables the bundling of Collision objects in a format readable by UE4."
    export.x_global_user_deletable = False

    export.data_fbx.axis_forward = "-Z"
    export.data_fbx.axis_up = "Y"
    export.data_fbx.global_scale = 1.0
    export.data_fbx.apply_unit_scale = True
    export.data_fbx.export_types = {'MESH', 'ARMATURE'}

    export.data_fbx.bake_anim_use_all_bones = True
    export.data_fbx.bake_anim_use_all_actions = True
    export.data_fbx.bake_anim_force_startend_keying = True
    export.data_fbx.optimise_keyframes = True

    tagHP = export.tags.add()
    tagHP.name = "High-Poly"
    tagHP.name_filter = "_HP"
    tagHP.name_filter_type = '1'
    tagHP.object_type = '2'
    tagHP.x_user_deletable = False
    tagHP.x_user_editable_type = True


    tagLP = export.tags.add()
    tagLP.name = "Low-Poly"
    tagLP.name_filter = "_LP"
    tagLP.name_filter_type = '1'
    tagLP.object_type = '2'
    tagLP.x_user_deletable = False
    tagLP.x_user_editable_type = True

    tagCG = export.tags.add()
    tagCG.name = "Cage"
    tagCG.name_filter = "_CG"
    tagCG.name_filter_type = '1'
    tagCG.object_type = '2'
    tagCG.x_user_deletable = False
    tagCG.x_user_editable_type = True

    tagCG.x_name_ext = "UCX_"
    tagCG.x_name_ext_type = '2'

    tagCX = export.tags.add()
    tagCX.name = "Collision"
    tagCX.name_filter = "_CX"
    tagCX.name_filter_type = '1'
    tagCX.object_type = '2'
    tagCX.x_user_deletable = False
    tagCX.x_user_editable_type = True

    # Special preference to rename objects during export, to make UE4/Unity export more seamless.
    tagCX.x_ue4_collision_naming = BoolProperty(default=True)

    tagAR = export.tags.add()
    tagAR.name = "Armature"
    tagAR.name_filter = "_AR"
    tagAR.name_filter_type = '1'
    tagAR.object_type = '7'
    tagAR.x_user_deletable = False
    tagAR.x_user_editable_type = False



    passOne = export.passes.add()
    passOne.name = "Combined Pass"
    passOne.export_animation_prev = False
    passOne.export_animation = False
    passOne.apply_modifiers = True
    passOne.triangulate = True

    # Ensure the new pass has all the current tags
    for tag in export.tags:
        newPassTag = passOne.tags.add()
        newPassTag.name = tag.name
        newPassTag.index = len(export.tags) - 1
        #newPassTag.use_tag = True

    passTwo = export.passes.add()
    passTwo.name = "Game-Ready Pass"
    passTwo.export_animation_prev = False
    passTwo.export_animation = False
    passTwo.apply_modifiers = True
    passTwo.triangulate = True

    i = 0

    # Ensure the new pass has all the current tags
    for tag in export.tags:
        newPassTag = passTwo.tags.add()
        newPassTag.name = tag.name
        newPassTag.index = len(export.tags) - 1

        #if i != 0:
            #newPassTag.use_tag = True

        i += 1

def CreatePresetUnity5Standard(exp):
    """
    Generates a saved preset for exporting assets compatible with Unity 5.
    """
    # -------------------------------------------------------------------------
    # Unity 5 Standard Template
    # -------------------------------------------------------------------------
    export = exp.add()
    export.name = "Unity 2017 Standard"
    export.description = "Creates an Export Preset for exporting FBX files for Unity 5, with optimised settings."
    export.x_global_user_deletable = False

    export.data_fbx.axis_forward = "Z"
    export.data_fbx.axis_up = "Y"
    export.data_fbx.global_scale = 1.0
    export.data_fbx.apply_scale_options = 'FBX_SCALE_UNITS'
    export.data_fbx.export_types = {'MESH', 'ARMATURE'}

    export.data_fbx.bake_anim_use_all_bones = True
    export.data_fbx.bake_anim_use_all_actions = True
    export.data_fbx.bake_anim_force_startend_keying = True
    export.data_fbx.optimise_keyframes = True

    tagLP = export.tags.add()
    tagLP.name = "Low-Poly"
    tagLP.name_filter = "_LP"
    tagLP.name_filter_type = '1'
    tagLP.x_user_deletable = False

    tagHP = export.tags.add()
    tagHP.name = "High-Poly"
    tagHP.name_filter = "_HP"
    tagHP.name_filter_type = '1'
    tagHP.x_user_deletable = False

    tagCG = export.tags.add()
    tagCG.name = "Cage"
    tagCG.name_filter = "_CG"
    tagCG.name_filter_type = '1'
    tagCG.x_user_deletable = False

    tagCX = export.tags.add()
    tagCX.name = "Collision"
    tagCX.name_filter = "_CX"
    tagCX.name_filter_type = '1'
    tagCX.x_user_deletable = False

    tagAR = export.tags.add()
    tagAR.name = "Armature"
    tagAR.name_filter = "_AR"
    tagAR.name_filter_type = '1'
    tagAR.object_type = '7'
    tagAR.x_user_deletable = False

    passOne = export.passes.add()
    passOne.name = "Combined Pass"
    passOne.export_animation_prev = False
    passOne.export_animation = False
    passOne.apply_modifiers = True
    passOne.triangulate = True

    # Ensure the new pass has all the current tags
    for tag in export.tags:
        newPassTag = passOne.tags.add()
        newPassTag.name = tag.name
        newPassTag.index = len(export.tags) - 1
        #newPassTag.use_tag = True

def CopyPreset(old_preset, new_preset):
    """
    Copies all the properties of one property into another given property.
    """

    for key in old_preset.keys():
        new_preset[key] = old_preset[key]

class CAP_DrawError(Operator):
    """
    ???
    """
    bl_idname = "cap.draw_error"
    bl_label = "Store Preset"

    title = StringProperty()
    message = StringProperty()

    def execute(self, context):
        bpy.context.window_manager.popup_menu(self.draw(context), title=self.title, icon='INFO')
        return {'FINISHED'}

    def draw(self, context):
        layout = self.layout
        col = layout.column()
        col.label(text="Custom Interface!")

        row = col.row()
        row.prop(self, "my_float")
        row.prop(self, "my_bool")

        col.prop(self, "my_string")


