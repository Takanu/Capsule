
import bpy
import copy

from bpy.types import Operator
from bpy.props import IntProperty, BoolProperty, FloatProperty, EnumProperty, PointerProperty, StringProperty, CollectionProperty

def DeletePresets():
    """
    Removes all Export Presets that that can be deleted by the user from the saved presets list.
    """
    print(">>>>>>>>>> Deleting presets...")
    preferences = bpy.context.preferences
    addon_prefs = preferences.addons[__package__].preferences
    exp = addon_prefs.saved_export_presets
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
    preferences = bpy.context.preferences
    addon_prefs = preferences.addons[__package__].preferences
    exp = addon_prefs.saved_export_presets
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
    CreatePresetUnityStandard(exp)

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
    export.export_animation = False

    export.data_fbx.axis_forward = "-Z"
    export.data_fbx.axis_up = "Y"
    export.data_fbx.global_scale = 1.0
    export.data_fbx.apply_unit_scale = True

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
    export.export_animation = False

    export.data_fbx.axis_forward = "-Z"
    export.data_fbx.axis_up = "Y"
    export.data_fbx.global_scale = 1.0
    export.data_fbx.apply_unit_scale = True
    export.data_fbx.export_types = {'MESH', 'ARMATURE'}

    export.data_fbx.bake_anim_use_all_bones = True
    export.data_fbx.bake_anim_use_all_actions = True
    export.data_fbx.bake_anim_force_startend_keying = True
    export.data_fbx.optimise_keyframes = True


def CreatePresetUnityStandard(exp):
    """
    Generates a saved preset for exporting assets compatible with Unity 5.
    """
    # -------------------------------------------------------------------------
    # Unity Standard Template
    # -------------------------------------------------------------------------
    export = exp.add()
    export.name = "Unity Standard"
    export.description = "Creates an Export Preset for exporting FBX files for Unity 5, with optimised settings."
    export.x_global_user_deletable = False
    export.export_animation = False

    export.data_fbx.axis_forward = "Z"
    export.data_fbx.axis_up = "Y"
    export.data_fbx.global_scale = 1.0
    export.data_fbx.apply_scale_options = 'FBX_SCALE_UNITS'
    export.data_fbx.export_types = {'MESH', 'ARMATURE'}
    export.data_fbx.bake_space_transform = True

    export.data_fbx.bake_anim_use_all_bones = True
    export.data_fbx.bake_anim_use_all_actions = True
    export.data_fbx.bake_anim_force_startend_keying = True
    export.data_fbx.optimise_keyframes = True


def CopyPreset(old_preset, new_preset):
    """
    Copies all the properties of one property into another given property.
    """

    for key in old_preset.keys():
        new_preset[key] = old_preset[key]

class CAPSULE_OT_DrawError(Operator):
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


