
import bpy
import copy

from bpy.types import Operator
from bpy.props import IntProperty, BoolProperty, FloatProperty, EnumProperty, PointerProperty, StringProperty, CollectionProperty

def DeletePresets():
    """
    Removes all Export Presets that that can be deleted by the user from the saved presets list.
    """
    #print(">>>>>>>>>> Deleting presets...")
    preferences = bpy.context.preferences
    addon_prefs = preferences.addons[__package__].preferences
    cap_file = addon_prefs.saved_export_presets
    presetsToKeep = []

    i = len(cap_file) - 1
    #print("i = ", i)

    while i != -1:
        item = cap_file[i]
        #print("item = ", item)
        if item.x_global_user_deletable is False:
            #print("Removing default cap_file...", cap_file[i])
            cap_file.remove(i)
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
    cap_file = addon_prefs.saved_export_presets
    sort = addon_prefs.sort_presets
    #print(">>>>>>>>>> Adding presets...")

    # Erase the previous sort entries (delayed)
    #print("Clearing sort presets")
    x = 0
    lenX = len(sort)
    while x < lenX:
        #print("Deleting sort preset...", sort[0])
        sort.remove(0)
        x += 1

    # Copy all the currently-saved presets to a temporary sort preset location.
    i = 0
    lenI = len(cap_file)
    #print("lenI = ", lenI)
    #print("lenI = ", lenI)
    #print("lenI = ", lenI)
    while i < lenI:
        if cap_file[0].x_global_user_deletable is True:
            #print("Copying user-defined preset...", cap_file[0])
            newPreset = sort.add()
            CopyPreset(cap_file[0], newPreset)

        #print("Deleting preset...", cap_file[0])
        cap_file.remove(0)
        i += 1

    # Create the new presets
    # CreatePresetDemo(cap_file)

    # Add the copied presets back
    i = 0
    lenI = len(sort)
    #print(sort)
    while i < lenI:
        #print("Adding back preset...", sort[0])
        newPreset = cap_file.add()
        CopyPreset(sort[0], newPreset)
        sort.remove(0)
        i += 1



def CreatePresetDemo(cap_file):
    """
    Generates a saved preset for exporting UE4-compatible assets.
    """
    # -------------------------------------------------------------------------
    # UE4 Standard Template
    # -------------------------------------------------------------------------
    export = cap_file.add()
    export.name = "Default Export Preset Demo"
    export.description = "Creates a tooltip for the preset."
    export.x_global_user_deletable = False
    
    # add options here!




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
        bpy.context.window_manager.popup_menu(self.draw(context), title=self.title, icon= 'INFO')
        return {'FINISHED'}

    def draw(self, context):
        layout = self.layout
        col = layout.column()
        col.label(text= "Custom Interface!")

        row = col.row()
        row.prop(self, "my_float")
        row.prop(self, "my_bool")

        col.prop(self, "my_string")


