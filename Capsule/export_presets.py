
import bpy
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
    export.axis_forward = "-Z"
    export.axis_up = "Y"
    export.global_scale = 1.0
    export.apply_unit_scale = True
    export.x_global_user_deletable = False

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
    export.axis_forward = "-Z"
    export.axis_up = "Y"
    export.global_scale = 1.0
    export.apply_unit_scale = True
    export.export_types = {'MESH', 'ARMATURE'}

    export.bake_anim_use_all_bones = True
    export.bake_anim_use_all_actions = True
    export.bake_anim_force_startend_keying = True
    export.optimise_keyframes = True

    export.x_global_user_deletable = False

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
    tagCX.x_ue4_collision_naming = True

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
    export.name = "Unity 5 Standard"
    export.description = "Creates an Export Preset for exporting FBX files for Unity 5, with optimised settings."
    export.axis_forward = "Z"
    export.axis_up = "Y"
    export.global_scale = 1.0
    export.apply_unit_scale = False
    export.export_types = {'MESH', 'ARMATURE'}

    export.bake_anim_use_all_bones = True
    export.bake_anim_use_all_actions = True
    export.bake_anim_force_startend_keying = True
    export.optimise_keyframes = True

    export.x_global_user_deletable = False
    export.x_unity_rotation_fix = True

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
    new_preset.name = old_preset.name
    new_preset.use_blend_directory = old_preset.use_blend_directory
    new_preset.use_sub_directory = old_preset.use_sub_directory
    new_preset.bundle_textures = old_preset.bundle_textures
    new_preset.filter_render = old_preset.filter_render
    new_preset.export_types = old_preset.export_types

    # OLD PASS COPYING
    for old_pass in old_preset.passes:
        new_pass = new_preset.passes.add()

        new_pass.name = old_pass.name
        new_pass.enable = old_pass.enable
        new_pass.file_suffix = old_pass.file_suffix
        new_pass.sub_directory = old_pass.sub_directory

        # OLD TAG COPYING
        for old_passtag in old_pass.tags:
            new_passtag = new_pass.tags.add()

            new_passtag.name = old_passtag.name
            new_passtag.prev_name = old_passtag.prev_name
            new_passtag.index = old_passtag.index
            new_passtag.use_tag = old_passtag.use_tag

        new_pass.export_individual = old_pass.export_individual
        new_pass.export_animation_prev = old_pass.export_animation
        new_pass.export_animation = old_pass.export_animation
        new_pass.apply_modifiers = old_pass.apply_modifiers
        new_pass.triangulate = old_pass.triangulate
        new_pass.use_tags_on_objects = old_pass.use_tags_on_objects

    new_preset.passes_index = old_preset.passes_index

    for old_tag in old_preset.tags:
        new_tag = new_preset.tags.add()

        new_tag.name = old_tag.name
        new_tag.name_filter = old_tag.name_filter
        new_tag.name_filter_type = old_tag.name_filter_type
        new_tag.object_type = old_tag.object_type
        new_tag.x_user_deletable = old_tag.x_user_deletable
        new_tag.x_user_editable_type = old_tag.x_user_editable_type
        new_tag.x_ue4_collision_naming = old_tag.x_ue4_collision_naming

    new_preset.tags_index = old_preset.tags_index

    new_preset.global_scale = old_preset.global_scale
    new_preset.bake_space_transform = old_preset.bake_space_transform
    new_preset.reset_rotation = old_preset.reset_rotation

    new_preset.axis_up = old_preset.axis_up
    new_preset.axis_forward = old_preset.axis_forward
    new_preset.apply_unit_scale = old_preset.apply_unit_scale

    new_preset.loose_edges = old_preset.loose_edges
    new_preset.tangent_space = old_preset.tangent_space

    new_preset.use_armature_deform_only = old_preset.use_armature_deform_only
    new_preset.add_leaf_bones = old_preset.add_leaf_bones
    new_preset.primary_bone_axis = old_preset.primary_bone_axis
    new_preset.secondary_bone_axis = old_preset.secondary_bone_axis
    new_preset.armature_nodetype = old_preset.armature_nodetype

    new_preset.bake_anim_use_all_bones = old_preset.bake_anim_use_all_bones
    new_preset.bake_anim_use_nla_strips = old_preset.bake_anim_use_nla_strips
    new_preset.bake_anim_use_all_actions = old_preset.bake_anim_use_all_actions
    new_preset.bake_anim_force_startend_keying = old_preset.bake_anim_force_startend_keying
    new_preset.use_default_take = old_preset.use_default_take
    new_preset.optimise_keyframes = old_preset.optimise_keyframes
    new_preset.bake_anim_step = old_preset.bake_anim_step
    new_preset.bake_anim_simplify_factor = old_preset.bake_anim_simplify_factor

    new_preset.x_unity_rotation_fix = old_preset.x_unity_rotation_fix

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


